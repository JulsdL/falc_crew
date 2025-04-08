from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from falc_crew.tools.custom_tool import FalcDocxWriterTool, FalcIconInjectorTool
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource


# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class FalcCrew():
    """FalcCrew crew"""

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools

    @agent
    def falc_translator(self) -> Agent:
        return Agent(
            config=self.agents_config['falc_translator'],
            tools=[FalcIconInjectorTool()],
            memory=True,
            verbose=True
        )

    @agent
    def falc_quality_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['falc_quality_analyst'],
            memory=True,
            verbose=True
        )

    @agent
    def falc_document_designer(self) -> Agent:
        return Agent(
            config=self.agents_config['falc_document_designer'],
            tools=[FalcDocxWriterTool()],
            memory=True,
            verbose=True
        )

    @agent
    def falc_visual_checker(self) -> Agent:
        return Agent(
            config=self.agents_config['falc_visual_checker'],
            memory=True,
            verbose=True
        )


    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def translate_text_task(self) -> Task:
        return Task(
            config=self.tasks_config['translate_text_task'],
        )

    @task
    def quality_check_task(self) -> Task:
        return Task(
            config=self.tasks_config['quality_check_task'],
        )

    @task
    def generate_docx_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_docx_task'],
        )

    @task
    def validate_visual_design_task(self) -> Task:
        return Task(
            config=self.tasks_config['validate_visual_design_task'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the FalcCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            memory=True,
            knowledge_sources=[
            TextFileKnowledgeSource(file_paths=["falc_guidelines.md"]),
            JSONKnowledgeSource(file_paths=["icons.json"])
            ]
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
