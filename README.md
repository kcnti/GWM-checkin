# GWM Auto Check in

An automated Python tool for daily check-ins to the "My GWM" mobile application. Earn points effortlessly with automatic authentication and daily check-in submissions to your Great Wall Motors account.

## Features

- **Automated Check-ins**: Performs daily check-ins automatically to earn points
- **Authentication**: Handles login and token management seamlessly
- **Points Tracking**: Monitors your current points balance

## Prerequisites

- Python 3.7+
- Valid GWM account credentials
- Device ID and GW ID from your vehicle/device

## Installation

1. Clone or download this repository
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy the environment file and configure your credentials:
   ```bash
   cp .env.example .env
   ```
4. Edit `.env` with your actual credentials

## Configuration

Update the `.env` file with your credentials:

```
APP_KEY=your_app_key
APP_SECRET=your_app_secret

DEVICE_ID=your_device_id
MODEL=your_vehicle_model
GW_ID=your_gw_id

USERNAME=your_username
PASSWORD=your_password
```

## Usage

Run the main script:

```bash
python main.py
```

The tool will:
1. Authenticate with your GWM account
2. Display your current points balance
3. Perform your daily check-in to earn points

## Files

- `main.py` - Main application with GWM API client
- `requirements.txt` - Python dependencies
- `.env.example` - Template for environment variables
- `gwm_login.json` - Generated file containing authentication tokens (created automatically)

## Troubleshooting

- **Token expired**: The tool automatically refreshes tokens when needed
- **Login elsewhere**: Handles cases where the account is logged in on another device

## License

This tool is for educational and debugging purposes only. Ensure compliance with GWM's terms of service.