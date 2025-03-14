from mistralai import Mistral

from app.config import get_settings

api_key = get_settings().MISTRAL_API_KEY
agent_id = get_settings().AGENT_ID


def create_prompt_check_code(user_code: str, sample_code: str):
    return f"""
    #### Code mẫu: 

    ```python
    {sample_code}
    ```

    #### Code người dùng:

    ```python
    {user_code}
    ```
    """.strip()


def run_prompt(prompt: str):
    client = Mistral(api_key=api_key)
    chat_response = client.agents.complete(
        agent_id=agent_id,
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    if chat_response.choices:
        return chat_response.choices[0].message.content
    else:
        return "No response from the agent."


if __name__ == "__main__":
    prompt = create_prompt_check_code(
        user_code="print('Hello, world!')",
        sample_code="print('Hello, world!')",
    )
    print(run_prompt(prompt))
