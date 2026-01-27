from app.workflows.article_workflow import ArticleWorkflow


def main():
    print(" LLM SEO Automation System")
    print("=" * 40)

    
    topic = input("Enter topic: ")

    workflow = ArticleWorkflow()
    result = workflow.run(topic)

    print("\n" + "=" * 40)
    print(" RAW ARTICLE:\n")
    print(result["raw_article"])

    print("\n" + "=" * 40)
    print(" SEO SEARCH QUERIES:\n")
    print(result["seo_queries"])

    print("\n" + "=" * 40)
    print(" FAQ BLOCK:\n")
    print(result["faq"])

    print("\n" + "=" * 40)
    print(" OPTIMIZED ARTICLE:\n")
    print(result["optimized_article"])


if __name__ == "__main__":
    main()
