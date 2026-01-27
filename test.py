from llm_seo_system.app.services.llm_service import LLMService

llm = LLMService()
result = llm.ask("Write short intro about LG laptops")
print(result)
