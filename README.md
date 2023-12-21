# ai4experiments-up-component
This repo contains the code of the unified-planning reusable component. This specific component installs all the planners and offers the operation modes as a GRPC service.

The aiplan4eu-unified-planning-server on the [ai4experiments platform](https://aiexp.ai4europe.eu) is created using the code in this repo.

## Interface with the component in the platform

To create a component that interfaces with the aiplan4eu-unified-planning-server follow the guidelines in the [up-graphene-engine](https://github.com/aiplan4eu/up-graphene-engine) repo.

## Create a new component modified

To actually on-board a new component in the platform the docker image must be created and pushed on an online platform (I used dockerhub), then a procedure very similar to the one to create a component that uses the [up-graphene-engine](https://github.com/aiplan4eu/up-graphene-engine) must be followed, which is explained in [these slides](https://docs.google.com/presentation/d/1v1R6OdxgOXRrMl8kgfoBc9Ug8xVnPpqz1BUVw3mskwo/edit#slide=id.g25ffcaa5279_1_21), from `On-Boarding a component 1/4`
to `On-Boarding a component 4/4`. The only modification is the location of the protobuf file, that is defined in the `unified-planning/unified_planning/grpc/unified_planning.proto` file.


After all desired steps are followed, the docker image must be built and pushed; an example of this can be found in the [push_on_docker.sh](https://github.com/aiplan4eu/ai4experiments-up-component/blob/master/push_on_docker.sh) file, that must be modified to push the image on your desired docker service.

#### Modify unified-planning version
The version of the unified-planning used by the component is the one added as a submodule in this repo, so to create another component that uses a different version it is enough to enter the unified-planning folder (cd unified-planning) and use git to move between branches and commits.

#### Modify installed engines
To install a different subset of engines there are 2 different paths, 1 for the default engines and one for non-default engines; the 2 procedures are not mutually exclusive so non-default engines can be installed with a subset of the default engines.

Note that the preference list of the factory can also be changed where the non-default engines are installed

##### Default engines:
In the [Dockerfile](https://github.com/aiplan4eu/ai4experiments-up-component/blob/master/Dockerfile) there is the line `RUN pip3 install ./unified-planning[engines]`; it is sufficient to modify this line with only the desired engines, for example: `RUN pip3 install ./unified-planning[aries,tamer,enhsp,fast-downward]`

##### Non-default engines:
To install non-default engines their integration must be installed in the Dockerfile (for example adding the line `RUN pip3 install up-fast-downward` to install the python package that connects the engine to the unified-planning)

Then, in the [server.py file](https://github.com/aiplan4eu/ai4experiments-up-component/blob/master/server.py), in the `UnifiedPlanningServer.__init__` method, the code to add an engine to the factory must be added.

[Here](https://unified-planning.readthedocs.io/en/latest/notebooks/tutorial/planner-integration.html#Registering-the-engine) is an example of how to add an engine to the `Factory`.

The added engine is by default at the end of the preference list, but the preference list can be set via file following [this procedure](https://unified-planning.readthedocs.io/en/latest/engines/02_engine_selection.html) or modified via python code using the `Factory.preference_list` `property` and `setter`.

## Library structure overview

##### Dependencies:
Python packages dependencies are defined in the `requirements.txt` file while other dependencies must be installed in the Dockerfile (for example the installation of OpenJDK-17)

##### GRPC Interface
The GRPC interface of the component is the one that is inside the `unified-planning/unified_planning/grpc/unified_planning.proto`; it defines both the protobuf structure used and the interface of the service exposed by this component.

##### Operation Mode services
The GRPC service is implemented in the `server.py` file, where every method defined by the protobuf server is implemented with the same name as a method of the `UnifiedPlanningServer` class.
