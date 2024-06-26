def get_llm_response_in_json(model_handler, prompt):
    try:
        # Generate response from the model
        resp = model_handler.generate_response(prompt)

        # Find the JSON part of the response
        first, last = resp.find("{"), resp.rfind("}")
        if first == -1 or last == -1:
            raise ValueError("JSON not found in the model response")
        
        # Extract and parse the JSON
        resp_json = json.loads(resp[first : last + 1], strict=False)
        return resp_json
    
    except json.JSONDecodeError as e:
        print("JSONDecodeError:", e)
        return {"error": "Invalid JSON format"}
    except ValueError as e:
        print("ValueError:", e)
        return {"error": str(e)}
    except Exception as e:
        print("Exception:", e)
        return {"error": "An error occurred"}