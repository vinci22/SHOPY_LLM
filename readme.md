Here is the entire response in the `README.md` format:

```markdown
# Chatbot - ShopyAgent

This project is a Django-based chatbot application that uses the OpenAI API to interact with users, providing them with information about products in a sample catalog. The chatbot has the ability to query product details and check availability in stock.

## Prerequisites

To run this project, you'll need the following:

- Python 3.7 or higher.
- An OpenAI account and your API key.
- Django installed.

## Installation

### 1. Clone the repository

First, clone this repository to your local machine:

```bash
git clone https://github.com/your_username/chatbot.git
cd chatbot
```

### 2. Set up a virtual environment (recommended)

It’s recommended to use a virtual environment to manage dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install dependencies

Once you’ve activated your virtual environment, install the required dependencies:

```bash
pip install -r requirements.txt
```

The dependencies are listed in the `requirements.txt` file, including `Django` and `openai` libraries.

### 4. Set up your OpenAI API key

You need to set your OpenAI API key to interact with the GPT-4 model. You can do this in several ways:

- **Via environment variable**:
  ```bash
  export OPENAI_API_KEY="your_openai_api_key"
  ```

- **Via `.env` file** (optional):
  You can create a `.env` file in the root of the project with the following content:
  ```
  OPENAI_API_KEY=your_openai_api_key
  ```

### 5. Set up the Django project

Run the following command to apply the initial migrations:

```bash
python manage.py migrate
```

### 6. Run the Django development server

Start the Django development server:

```bash
python manage.py runserver
```

You can now access the chatbot application by navigating to `http://127.0.0.1:8000/` in your web browser.

## Usage

Once the Django server is running, you can interact with the chatbot via the web interface.

The `ShopyAgent` class in `agent.py` handles the chatbot's logic, interacting with the OpenAI API. The main functions of the chatbot are:

1. **get_product_info**: Fetches details about a specific product.
2. **check_stock**: Checks if a product is available in the inventory.

### Example usage within Django views

Here’s an example of how the chatbot logic can be integrated into Django views:

```python
from django.http import JsonResponse
from .agent import ShopyAgent

def chatbot_view(request):
    user_message = request.GET.get("message", "")
    agent = ShopyAgent()
    response = agent.run(user_message)

    return JsonResponse({"response": response})
```

### URL Configuration

You can map the `chatbot_view` to a URL in your `urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('chatbot/', views.chatbot_view, name='chatbot'),
]
```

With this setup, you can send a GET request to `/chatbot/?message=<your_message>` to interact with the chatbot.

## Project Structure

```
chatbot/
├── chatbot/
│   ├── __init__.py
│   ├── agent.py             # Main file with the chatbot logic
│   ├── views.py             # Views handling chatbot logic
│   ├── urls.py              # URL routing for the chatbot
│   ├── settings.py          # Django settings
│   ├── models.py            # Django models (if needed)
│   ├── migrations/          # Django migration files
├── manage.py                # Django management script
├── requirements.txt         # Project dependencies
└── README.md                # This file
```

## ShopyAgent Class Overview

The `ShopyAgent` class is responsible for handling the chatbot's operations, including retrieving product information and checking stock availability. Here’s a breakdown of the class:

```python
import os
import openai

# Configure OpenAI API key
openai_api_key = os.environ.get("OPENAI_API_KEY")

class ShopyAgent:
    def __init__(self):
        self.product_catalog = [
            {"name": "Laptop", "description": "High-performance laptop", "price": 999.99, "stock": 10},
            {"name": "Smartphone", "description": "Latest model smartphone", "price": 699.99, "stock": 5},
            {"name": "Headphones", "description": "Noise-cancelling headphones", "price": 149.99, "stock": 0}
        ]

    # Fetch product information by name
    def get_product_info(self, product_name):
        for product in self.product_catalog:
            if product["name"].lower() == product_name.lower():
                return product
        return None

    # Check if product is in stock
    def check_stock(self, product_name):
        product = self.get_product_info(product_name)
        if product:
            if product["stock"] > 0:
                return f"Yes, the '{product['name']}' is available with {product['stock']} units in stock."
            else:
                return f"Unfortunately, the '{product['name']}' is currently out of stock."
        return f"I'm sorry, I couldn't find a product named '{product_name}'." 

    # Define the functions available to the model
    def get_functions(self):
        return [
            {
                "name": "get_product_info",
                "description": "Fetches product details from the catalog.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_name": {"type": "string", "description": "The name of the product."}
                    },
                    "required": ["product_name"],
                },
            },
            {
                "name": "check_stock",
                "description": "Checks if a product is in stock.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_name": {"type": "string", "description": "The name of the product."}
                    },
                    "required": ["product_name"],
                },
            },
        ]

    # Conversational flow
    def run(self, message):
        conversation_history = []
        user_input = message

        # Add user input to conversation history
        conversation_history.append({"role": "user", "content": user_input})

        # Call OpenAI API for response
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=conversation_history,
            functions=self.get_functions(),
            function_call="auto",
        )

        # Extract assistant message
        assistant_message = response.choices[0].message

        # Execute function if called
        if "function_call" in assistant_message:
            function_name = assistant_message["function_call"]["name"]
            arguments = eval(assistant_message["function_call"]["arguments"])

            if function_name == "get_product_info":
                product_name = arguments.get("product_name")
                product = self.get_product_info(product_name)
                if product:
                    result = (
                        f"Here's what I found about '{product['name']}':\n"
                        f"- Description: {product['description']}\n"
                        f"- Price: ${product['price']:.2f}\n"
                        f"- Stock: {'Available' if product['stock'] > 0 else 'Out of stock'}"
                    )
                else:
                    result = f"I'm sorry, I couldn't find any product named '{product_name}'." 
            elif function_name == "check_stock":
                product_name = arguments.get("product_name")
                result = self.check_stock(product_name)
            else:
                result = "Oops! This function isn't implemented yet."

            # Add function response to conversation history
            conversation_history.append(
                {"role": "function", "name": function_name, "content": result}
            )

            # Get the assistant's final response
            response = openai.ChatCompletion.create(
                model="gpt-4-0613",
                messages=conversation_history,
                functions=self.get_functions(),
                function_call="none",
            )
            assistant_message = response.choices[0].message

        # Add assistant message to conversation history
        conversation_history.append({"role": "assistant", "content": assistant_message['content']})

        # Return the assistant's response
        return assistant_message['content']
```

## Contributing

If you'd like to contribute to this project, you can fork the repository, create a branch with your changes, and submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
```

This `README.md` file provides clear instructions for setting up and running the Django application, along with a detailed explanation of the `ShopyAgent` class used in the chatbot logic. It includes all necessary dependencies, setup steps, and examples for integrating the chatbot into Django views.