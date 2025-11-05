# Use Alpine as base image
FROM alpine

# Set environment variables
ENV LLAMA_CPP_DIR=/llama.cpp

# Install dependencies
RUN apk add --no-cache \
    git \
    build-base \
    make \
    wget \
    curl

# Clone llama.cpp repository
RUN git clone https://github.com/ggerganov/llama.cpp.git ${LLAMA_CPP_DIR}

# Set working directory
WORKDIR ${LLAMA_CPP_DIR}

RUN apk add --no-cache cmake
RUN apk add --no-cache curl-dev
RUN apk add --no-cache linux-headers
# Build llama.cpp
RUN cmake -B build
RUN cmake --build build --config Release

# Create directory for models
RUN mkdir -p /models

# Expose the default server port
EXPOSE 8080
# Set the default command to run the server
ENTRYPOINT ["/llama.cpp/build/bin/llama-server"] 
CMD ["--jinja", "-m", "/models/qwen2.5-3b-instruct-q4_k_m.gguf", "--host", "0.0.0.0", "--port", "8080", "--ctx-size", "16384" , "--cache-ram", "0"]