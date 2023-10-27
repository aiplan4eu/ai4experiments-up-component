from concurrent import futures

import logging
import time
import grpc

import unified_planning
from unified_planning.engines.results import POSITIVE_OUTCOMES
from unified_planning.shortcuts import Problem, OneshotPlanner
import unified_planning.grpc.generated.unified_planning_pb2 as op_pb2
import unified_planning.grpc.generated.unified_planning_pb2_grpc as op_pb2_grpc
from unified_planning.grpc.proto_reader import  ProtobufReader
from unified_planning.grpc.proto_writer import  ProtobufWriter

from unified_planning.shortcuts import *

class UnifiedPlanningServer(op_pb2_grpc.UnifiedPlanningServicer):
    def __init__(self, port):
        self.port = port

        self.log_format = (
            '[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s')
        self.logger = logging.getLogger("Unified Planning Service")
        logging.basicConfig(level=logging.INFO, format=self.log_format)
        self.reader = ProtobufReader()
        self.writer = ProtobufWriter()

    def planAnytime(self, request, context):
        self.logger.info("Received anytime request")
        problem = self.reader.convert(request.problem)
        # TODO add resolution_mode and timeout
        self.logger.info("Converted problem")
        with AnytimePlanner(problem_kind=problem.kind, anytime_guarantee="INCREASING_QUALITY") as planner:
            self.logger.info("Got anytime planner, getting solutions")
            for p in planner.get_solutions(problem):
                self.logger.info("Got anytime planner, getting solutions")
                next_result = self.writer.convert(p)
                self.logger.info("Sending a solution")
                yield next_result
                self.logger.info(f"Sent res: {next_result}")
            self.logger.info("Finished solutions")

    def planOneShot(self, request, context):
        problem = self.reader.convert(request.problem)
        # TODO add resolution_mode and timeout
        with OneshotPlanner(problem_kind=problem.kind) as planner:
            result = planner.solve(problem)
            if result.status in unified_planning.engines.results.POSITIVE_OUTCOMES:
                self.logger.info(f"{planner.name} found this plan: {result.plan}")
            else:
                self.logger.info("No plan found.")
            answer = self.writer.convert(result)
        return answer

    def validatePlan(self, request, context):
        problem = self.reader.convert(request.problem)
        plan = self.reader.convert(request.plan)
        with PlanValidator(problem_kind=problem.kind, plan_kind=plan.kind) as validator:
            validation_result = validator.validate(problem, plan)
            answer = self.writer.convert(validation_result)
            return answer

    def compile(self, request, context):
        problem = self.reader.convert(request)
        # TODO: This should be supplied with request
        ck = CompilationKind.GROUNDING
        with Compiler(
            problem_kind=problem.kind,
            compilation_kind=ck
        ) as compiler:
            result = compiler.compile(problem)
            answer = self.writer.convert(result)
            return answer

    def start(self):
        connection = '0.0.0.0:%d' % (self.port)
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        op_pb2_grpc.add_UnifiedPlanningServicer_to_server(
            self, self.server)
        self.server.add_insecure_port(connection)
        self.server.start()
        self.logger.info("server started on %s" % connection)

    def wait_for_termination(self):
        self.server.wait_for_termination()
