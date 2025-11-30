import os
from litellm import completion

class NL2SQLService:
    def __init__(self):
        self.model = "gemini/gemini-2.0-flash"
        # Ensure API key is set
        if not os.getenv("GEMINI_API_KEY"):
             print("Warning: GEMINI_API_KEY not set")

    def generate_sql(self, user_query: str) -> str:
        schema_desc = """
        PostgreSQL Database Schema:
        Schema: api_catalog
        
        Table: api
        Columns:
        - api_id (INT, PK)
        - api_name (TEXT)
        - description (TEXT)
        - base_url (TEXT)
        - auth_type (TEXT) -- e.g., "ApiKey", "OAuth", "None"
        - https_supported (BOOLEAN)
        - cors_supported (BOOLEAN)
        - pricing_tier (TEXT) -- e.g., "Free", "Paid"
        - category_id (INT, FK -> category.category_id)
        
        Table: category
        Columns:
        - category_id (INT, PK)
        - category_name (TEXT)
        
        Relationships:
        - api.category_id references category.category_id
        """
        
        prompt = f"""
        You are an expert SQL assistant.
        Given the following database schema, generate a valid PostgreSQL SELECT query to answer the user's question.
        
        {schema_desc}
        
        User Question: {user_query}
        
        Rules:
        1. Return ONLY the SQL query. No markdown, no explanations.
        2. Use the schema `api_catalog` for table names (e.g., `api_catalog.api`).
        3. Use ILIKE for text comparisons.
        4. ALWAYS select the following columns for API results: `a.api_id`, `a.api_name`, `a.description`, `a.auth_type`, `a.https_supported`, `a.cors_supported`, `a.pricing_tier`. Join with category if needed to get `c.category_name`.
        5. If the question cannot be answered, return "CANNOT_ANSWER".
        """
        
        try:
            response = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                custom_llm_provider="gemini"
            )
            
            content = response.choices[0].message.content.strip()
            # Clean up markdown code blocks if present
            if content.startswith("```"):
                lines = content.split("\n")
                # Remove first line (```sql) and last line (```)
                if len(lines) >= 3:
                    content = "\n".join(lines[1:-1])
                else:
                    content = content.replace("```", "")
            
            return content.strip()
        except Exception as e:
            print(f"Error generating SQL: {e}")
            return "ERROR"
