# Message verificator

Storyteller is a project that generates a story from a random frame of your video. It uses machine learning algorithms to analyze the frame and generate a relevant story.

## Prerequisites

-   Docker

## Getting Started

To get a local copy up and running, follow these steps:

1. Clone the repository:

```bash
git clone https://github.com/w1sq/message_verificator.git
```

2. Navigate to the project directory:

```bash
cd message_verificator
```

3. Build the Docker image:

```bash
docker build -t message_verificator .
```

4. Run the Docker container:

```bash
docker run -p 8501:8501 message_verificator
```

After running these commands, open your web browser and navigate to Network URL from console to view the Streamlit app.

## Usage

Upload your video file in the Streamlit app. The app will select a random frame from the video, generate a story based on the frame, and display the story.

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

## License

Distributed under the [MIT License](LICENSE). See `LICENSE` for more information.

## Contact

Kokorev Artem - <kokorev_artem@vk.com>
