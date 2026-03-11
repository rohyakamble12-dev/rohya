# Project Structure Guide

This document outlines the directory layout for the Rohya project.

## Directory Structure
```
rohya/
├── docs/
│   └── PROJECT_STRUCTURE.md  # Project structure documentation
├── src/
│   ├── main/
│   │   └── java/            # Main application code
│   └── test/
│       └── java/            # Unit tests
├── resources/                # Supporting resources (config files, etc.)
├── libs/                     # External libraries
├── bin/                      # Compiled binaries
└── README.md                 # Project overview and instructions
```

## Directory Description
- `docs/`: Contains documentation files related to the project.
- `src/`: The main source code follows a standard structure with separate directories for main application code and tests.
- `resources/`: Houses optional configurations and resources used by the application.
- `libs/`: A place for third-party libraries.
- `bin/`: Stores compiled binaries generated after a build process.
- `README.md`: Basic information, project description, and instructions to get started.

## Setup Guide
1. **Clone the Repository**:  
   ```bash
   git clone https://github.com/rohyakamble12-dev/rohya.git
   cd rohya
   ```
2. **Install Dependencies**: 
   Ensure you have the necessary development tools and dependencies installed.
   - For Java: Make sure to use Java 11 or above. You can use [SDKMAN!](https://sdkman.io/) for a simple installation.
   ```bash
   sdk install java 11.0.11-open
   ```
3. **Build the Project**:  
   Use a build tool like Maven or Gradle to build the project. Here’s an example with Maven:
   ```bash
   mvn clean install
   ```
4. **Run the Application**:  
   After building, run the application from the command line.
   ```bash
   java -jar target/rohya.jar
   ```
5. **Explore Further**: 
   - Refer to `docs/` for more detailed information and documentation as the project grows.