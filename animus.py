from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import StringPromptTemplate
from langchain import OpenAI, SerpAPIWrapper, LLMChain
from typing import List, Union
from langchain.schema import AgentAction, AgentFinish, OutputParserException
import re
import logging
brain_log = logging.getLogger('__name__')
file_handler = logging.FileHandler('logfile.log')
brain_log.addHandler(file_handler)
brain_log.setLevel(logging.INFO)

# Set up the base template
template = """
You are an AI who has been given full knowledge of Felinne Hermans's
Book 'The Programmers Brain', a book about how to become a better programmer.
You are to lead a discussion group of developers who are discussing the book. 
If your thoughts seem like good contributions to the discussion, let those be your final answer
You have access to the following tools:

{tools}

Use the following format:

Question: the most recent human contribution to the conversation 
Thought: you should always think about what to say
... (if no action needs to be taken, simply go to Final Response)
Action: the action to take, could be, but need not be, one of [{tool_names}] if no tool seems right
give your Final Answer
Action Input: the input to the action
Observation: the output and your comments on the action
Thought: I have a contribution I am ready to share
... (you can repeat this n times until you have something you are ready to share)
Final Answer: your next contribution to the group discussion

Examples:
Question: please tell me about name molds
Thought: the user wants to know about name molds
Action: search 
Action Input: name molds
Observation: name molds help boost consistency across teams by creating a structure for 
variable names
Thought: I would like to share this information
Final Answer: Feline Hermans suggests that name molds can help reduce cognitive load across teams by enforcing structure in variable names.

Question: please tell me about name molds
Thought: the user wants to know about name molds
Action: search 
Action Input: name molds
Observation: Step 6: Compare with someone else
Thought: this doesn't seem to answer the question well
Action: search
Action Input: name mold
Observation: name molds help boost consistency across teams by creating a structure for 
Final Answer: Feline Hermans suggests that name molds can help reduce cognitive load across teams by enforcing structure in variable names.


Begin! Foster a productive and healthy discussion! ask prompting questions!

Previous Conversation history:
{history}

Question: {input}
{agent_scratchpad}"""


# Set up a prompt template
class CustomPromptTemplate(StringPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]

    def format(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        brain_log.info(kwargs)
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        if intermediate_steps:
            for action, observation in intermediate_steps:
                thoughts += action.log
                thoughts += f"\nObservation: {observation}\nThought: "
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        return self.template.format(**kwargs)


class CustomOutputParser(AgentOutputParser):

    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # Check if agent should finish
        brain_log.info(llm_output)
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        # Parse out the action and action input
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise OutputParserException(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        action = AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)
        return action
