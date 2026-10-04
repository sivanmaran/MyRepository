import ollama


def main() -> None:
	client = ollama.Client()
	response = client.chat(
		model="qwen2.5:7B",
		messages=[
			{"role": "user", "content": "what is 10 + 20."}
		]
	)
	print(response["message"]["content"])


if __name__ == "__main__":
	main()
