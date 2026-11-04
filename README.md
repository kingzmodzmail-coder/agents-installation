# Agents Installation Repository

This repository provides installation instructions, setup scripts, and examples for deploying AI agents, with a focus on decision models (System 1 models) and integration with tools like Grok bots.

## Overview

Decision models such as Jev from TypeSafe are optimized for fast, structured decisions (yes/no, choice, score) rather than natural language generation. They are ideal for high-volume background automation in agent pipelines.

## Prerequisites

- Python 3.10+
- Git
- Optional: Docker, API keys for providers (TypeSafe/Jev, OpenAI, etc.)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/kingzmodzmail-coder/agents-installation.git
   cd agents-installation
   ```

2. Run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. Configure environment variables in `.env` (copy from `.env.example`).

## Decision Models

Refer to the NetworkChuck video on Jev for concepts: fast System 1 decisions for spam classification, routing, scoring, etc.

Example usage scripts are in the `examples/` directory.

## Grok Bots Integration

This setup supports connecting agents to Grok bots for persistent memory and scheduled routines. See `docs/grok-bots.md`.

## Contributing

Pull requests welcome. Keep setups hardware-accurate and minimal where possible.
