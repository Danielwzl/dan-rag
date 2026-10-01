                 Question
                     │
                     ▼
             nomic-embed-text
                     │
                     ▼
              Query Vector
                     │
                     ▼
                ChromaDB
                     │
                     ▼
               Top 3 chunks
                     │
                     ▼
              Context Builder
                     │
                     ▼
                  Prompt
                     │
                     ▼
              DeepSeek-R1 8B
                     │
                     ▼
                  Answer



                 User
                  │
                  ▼
             AI Assistant
                  │
        ┌─────────┴─────────┐
        │                   │
   Understanding        Analytics
        │                   │
   DeepSeek/RAG          DuckDB
        │                   │
        └─────────┬─────────┘
                  │
             Data Layer
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
     CSV        XLSX       Recipes
