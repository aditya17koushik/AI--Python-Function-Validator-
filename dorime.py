#IMPORTING LIBRARIES,PACKAGES AND DEPENDENCIES
from flask import Flask, request, jsonify
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

app = Flask(__name__)

# OpenAI API key setup
openai_api_key = 'YOUR_API_KEY'
chat_model = ChatOpenAI(api_key=openai_api_key, model="gpt-4", temperature=0)


@app.route('/validate_function', methods=['POST'])
def validate_function():
    try:
        # Detect input type from Postman
        content_type = request.content_type

        if content_type == 'application/json':
            # JSON input
            data = request.get_json()
            python_function = data.get('function_code')
            function_description = data.get('function_description')

        elif content_type == 'text/plain':
            # Raw text input
            python_function = request.data.decode('utf-8')
            function_description = 'No description provided (text input).'

        elif 'multipart/form-data' in content_type:
            # Form-Data input (file upload + description)
            uploaded_file = request.files.get('file')
            function_description = request.form.get('function_description', 'No description provided.')

            if not uploaded_file:
                return jsonify({'error': 'File is required for form-data input'}), 400

            python_function = uploaded_file.read().decode('utf-8')

        elif content_type == 'application/octet-stream':
            # Binary input
            python_function = request.data.decode('utf-8')
            function_description = 'No description provided (binary input).'

        else:
            return jsonify({'error': f'Unsupported Content-Type: {content_type}'}), 400

        # Check if function code is empty
        if not python_function:
            return jsonify({'error': 'Python function code is required'}), 400

        # Prepare GPT prompt using LangChain
        messages = [
            SystemMessage(content="You are an expert Python code auditor."),
            HumanMessage(content=f"Validate the following Python function against its description.\n\n"
                                 f"Function Description: {function_description}\n\n"
                                 f"Python Function:\n{python_function}\n\n"
                                 "Analyze the code and check if it correctly implements the described functionality. "
                                 "Provide a detailed analysis, including correctness, potential errors, edge cases, and suggestions for improvement. "
                                 "Return the response in JSON format with fields: matches_description, observations (list), improvements (list).")
        ]

        # Call GPT model via LangChain
        response = chat_model.invoke(messages)

        analysis = response.content.strip()

        return jsonify({'analysis': analysis})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
