
import os
import openai
# Configura tu clave API de OpenAI
openai_api_key = os.environ.get("OPENAI_API_KEY")


class ShopyAgent:
    def __init__(self):
        self.product_catalog = [
    {"name": "Laptop", "description": "High-performance laptop", "price": 999.99, "stock": 10},
    {"name": "Smartphone", "description": "Latest model smartphone", "price": 699.99, "stock": 5},
    {"name": "Headphones", "description": "Noise-cancelling headphones", "price": 149.99, "stock": 0}
]


    # Función para obtener detalles de un producto
    def get_product_info(self, product_name):
        for product in self.product_catalog:
            if product["name"].lower() == product_name.lower():
                return product
        return None

    # Función para verificar la disponibilidad de un producto
    def check_stock(self, product_name):
        product = self.get_product_info(product_name)
        if product:
            if product["stock"] > 0:
                return f"Yes, the '{product['name']}' is available with {product['stock']} units in stock."
            else:
                return f"Unfortunately, the '{product['name']}' is currently out of stock."
        return f"I'm sorry, I couldn't find a product named '{product_name}'."

    # Definición de funciones para el modelo
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

    # Conversación con el usuario
    def run(self, message):
        
        conversation_history = []

        user_input = message

        # Agregar el mensaje del usuario al historial
        conversation_history.append({"role": "user", "content": user_input})

        # Llamar a la API de OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=conversation_history,
            functions=self.get_functions(),
            function_call="auto",  # Permitir al modelo decidir si llama una función
        )

        # Acceder a la respuesta del asistente
        assistant_message = response.choices[0].message

        # Si el modelo llama una función
        if "function_call" in assistant_message:
            function_name = assistant_message["function_call"]["name"]
            arguments = eval(assistant_message["function_call"]["arguments"])

            # Ejecutar la función correspondiente
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

            # Agregar la respuesta de la función al historial
            conversation_history.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": result,
                }
            )

            # Actualizar la respuesta del asistente después de llamar la función
            response = openai.ChatCompletion.create(
                model="gpt-4-0613",
                messages=conversation_history,
                functions=self.get_functions(),
                function_call="none",  # No permite más llamadas en este turno
            )
            assistant_message = response.choices[0].message

        # Agregar el mensaje del asistente al historial
        conversation_history.append({"role": "assistant", "content": assistant_message['content']})

        # Mostrar la respuesta del asistente
        # print(f"ShopBot: {assistant_message['content']}")
        return assistant_message['content']


