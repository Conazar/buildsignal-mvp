from typing import List
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableSequence
import os
from dotenv import load_dotenv
load_dotenv()

from prompts import BUILD_SIGNAL_SYSTEM_PROMPT

# =========================================================
# CONFIG
# =========================================================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

MODEL_NAME = "gemini-2.5-flash-lite"


# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = BUILD_SIGNAL_SYSTEM_PROMPT


# =========================================================
# OUTPUT SCHEMA
# =========================================================

class BuildSignal(BaseModel):
    signal: str
    reasoning: str


class ScoredSection(BaseModel):
    score: int = Field(..., ge=1, le=10)
    reasoning: str
    evidence: List[str]


class ExecutionStyle(BaseModel):
    primary_style: str
    secondary_traits: List[str]
    reasoning: str


class ExecutionProfile(BaseModel):
    build_signals: List[BuildSignal]

    learning_velocity: ScoredSection

    systems_thinking: ScoredSection

    execution_style: ExecutionStyle

    adaptability: ScoredSection

    complexity_handling: ScoredSection

    behavioral_patterns: List[str]

    strengths: List[str]

    risk_signals: List[str]

    evidence_summary: List[str]

    overall_assessment: str


# =========================================================
# OUTPUT PARSER
# =========================================================

parser = JsonOutputParser(pydantic_object=ExecutionProfile)


# =========================================================
# MODEL
# =========================================================

llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    google_api_key=GOOGLE_API_KEY,
    temperature=0.3,
)


# =========================================================
# PROMPT TEMPLATE
# =========================================================

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", """
Analyze the following activity and generate an execution profile.

ACTIVITY:
{activity}

Return ONLY valid JSON.

{format_instructions}
"""),
    ],
    template_format="jinja2"
).partial(
    format_instructions=parser.get_format_instructions()
)


# =========================================================
# CHAIN
# =========================================================

chain: RunnableSequence = (
    prompt
    | llm
    | parser
)


# =========================================================
# ANALYZER FUNCTION
# =========================================================

def analyze_activity(activity: str):
    response = chain.invoke(
        {
            "activity": activity
        }
    )

    return response


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    sample_input = """
Built AI workflow automations using Python and FastAPI.
Participated in hackathons.
Rapidly learned async systems and LLM orchestration.
Experimenting with ERP automation and CRM workflows.
Runs online communities and studies internet growth systems.
"""

    result = analyze_activity(sample_input)

    import json

    print(json.dumps(result, indent=2))


"""OUTPUT -
{
  "build_signals": [
    {
      "signal": "Systems-oriented operational thinking",
      "reasoning": "The user's activity involves building and integrating AI workflows, indicating a focus on how different components interact and function together to achieve a larger goal. This suggests an understanding of system architecture and operational flow."
    },
    {
      "signal": "Automation-driven problem solving",
      "reasoning": "The explicit mention of 'building AI workflows' points to a proactive approach in leveraging automation to solve problems or create new capabilities, rather than relying on manual processes."
    },
    {
      "signal": "Experimentation with new technologies",
      "reasoning": "Engaging with 'new AI models and tools' implies a willingness to explore and test emerging technologies to understand their potential applications and limitations."
    },
    {
      "signal": "Iterative development approach",
      "reasoning": "The process of 'refining prompts and parameters' suggests an iterative cycle of testing, evaluating, and adjusting to improve outcomes, which is characteristic of an iterative execution style."
    },
    {
      "signal": "Curiosity-driven exploration",
      "reasoning": "Exploring 'various use cases' and 'different AI models' demonstrates a broad curiosity and a desire to understand the landscape of AI capabilities and their potential applications."
    }
  ],
  "learning_velocity": {
    "score": 7,
    "reasoning": "The user actively engages with and experiments with new AI models and tools, and refines parameters, indicating a rapid pace of learning and practical application of new technologies.",
    "evidence": [
      "Experimented with new AI models and tools",
      "Refined prompts and parameters to improve outcomes",
      "Explored various use cases"
    ]
  },
  "systems_thinking": {
    "score": 7,
    "reasoning": "Building AI workflows and integrating different components suggests an ability to conceptualize and construct interconnected systems to achieve specific objectives.",
    "evidence": [
      "Built AI workflows",
      "Integrated different components to achieve desired outputs"
    ]
  },
  "execution_style": {
    "primary_style": "Iterative Builder",
    "secondary_traits": [
      "Experimentation-driven",
      "Systems-oriented",
      "Automation-focused"
    ],
    "reasoning": "The user's activity centers around building, experimenting with, and refining AI workflows. This iterative process of testing, adjusting parameters, and integrating components to achieve desired outputs defines an iterative builder who leverages experimentation and automation within a systems context."
  },
  "adaptability": {
    "score": 6,
    "reasoning": "The user demonstrates adaptability by exploring various AI models and tools and adjusting their approach (prompts, parameters) based on experimentation to achieve desired outcomes. This suggests a capacity to adjust strategies in response to new information or technological capabilities.",
    "evidence": [
      "Experimented with new AI models and tools",
      "Refined prompts and parameters to improve outcomes",
      "Explored various use cases"
    ]
  },
  "complexity_handling": {
    "score": 5,
    "reasoning": "The user engages with AI models and workflows, which can involve understanding parameters, prompt engineering, and integration. While not explicitly detailing highly complex systems, the activity suggests a moderate ability to handle the intricacies of AI tool usage and workflow construction.",
    "evidence": [
      "Built AI workflows",
      "Integrated different components",
      "Refined prompts and parameters"
    ]
  },
  "behavioral_patterns": [
    "Proactive experimentation with emerging technologies",
    "Iterative refinement of technical processes",
    "Systems integration for functional outcomes",
    "Problem-solving through automation",
    "Exploratory learning across diverse applications"
  ],
  "strengths": [
    "Rapid adoption and application of new AI technologies",
    "Ability to construct and optimize automated workflows",
    "Systems-level thinking in AI implementation",
    "Iterative approach to problem-solving and improvement"
  ],
  "risk_signals": [
    "Potential for over-reliance on specific AI models without deep foundational understanding (inferred from focus on tools/workflows)",
    "Limited evidence of long-term project execution or impact beyond experimentation (inferred from description of activity)"
  ],
  "evidence_summary": [
    "Built AI workflows.",
    "Experimented with new AI models and tools.",
    "Integrated different components to achieve desired outputs.",
    "Refined prompts and parameters to improve outcomes.",
    "Explored various use cases."
  ],
  "overall_assessment": "The individual demonstrates a strong capacity for hands-on experimentation and iterative development within the AI domain. They exhibit a builder mindset, actively engaging with new technologies to construct and refine automated workflows. Their approach suggests systems thinking and a drive to leverage AI for problem-solving. Learning velocity appears high due to continuous exploration and adaptation of parameters. While adept at operationalizing AI tools, the evidence does not yet clearly indicate the scale or long-term impact of their work."
}
 """