# University Course Project: Data Analysis and Visualization

## Overview

This repository is part of a university course project focused on analyzing and visualizing data from YouTube and Telegram. The project is split into three main teams:

- **Data Loading Team - YouTube**: Responsible for extracting data from YouTube.
- **Data Loading Team - Telegram**: Responsible for extracting data from Telegram.
- **Data Analysis and Visualization Team**: Responsible for computing metrics, storing them in a PostgreSQL database, and visualizing them using Grafana.

This repository is managed by the Data Analysis and Visualization Team. It serves as a monorepo that contains all the necessary components to precompute metrics from YouTube and Telegram data and load them into PostgreSQL for visualization.

## Repository Structure

The repository is organized into two main folders:

- **YouTube**: Contains the subrepository and specific instructions related to YouTube data processing.
- **Telegram**: Contains the subrepository and specific instructions related to Telegram data processing.

Each folder has its own README.md file that provides detailed instructions on how to handle the data specific to that platform.

## Main Goals

The primary goals of this repository are to:

1.  **Precompute Metrics**: Calculate specific metrics from the data provided by the YouTube and Telegram teams.
2.  **Store Metrics in PostgreSQL**: Load the computed metrics into a PostgreSQL database for persistent storage.

## Getting Started

To start working with each subrepository, follow steps in its README.

## Contributions

If you wish to contribute to this repository, please make a Pull Request. It must contain a detailed description explaining the reasoning behind the changes. In your description, mention why you proposed this Pull Request and what is the intended behavior of your code. This helps maintainers understand your contributions and ensures alignment with the project's goals.

## Support

For any issues or questions, refer to the FAQs in each subrepository's README or contact the project maintainers.
