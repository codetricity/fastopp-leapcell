# FastOpp PostgreSQL Edition - LeapCell Deployment Tutorial

This tutorial provides step-by-step instructions for deploying the FastOpp PostgreSQL Edition to LeapCell, leveraging its free tier for educational purposes.

## Prerequisites

* A GitHub account with this repository forked
* A LeapCell account (sign up at [leapcell.io](https://leapcell.io/))

## Setup Steps

### 1. Create a New Project on LeapCell

* Log in to your LeapCell account
* Navigate to the dashboard and click "New Project"
* Select "Connect to GitHub" and choose your forked repository
* Follow the prompts to set up the basic project

### 2. Create a PostgreSQL Database Service

* In your LeapCell project dashboard, go to the "Database" section (left sidebar)
* Click on "Create New Database" or similar option
* Choose "PostgreSQL" as the database type
* LeapCell will provision a new PostgreSQL instance and provide you with a `DATABASE_URL`
* **Copy this DATABASE_URL** - you'll need it for environment variables

### 3. Create an Object Storage Service

* In your LeapCell project dashboard, go to the "Object Storage" section (left sidebar)
* Click on "Create New Object Storage" or similar option
* LeapCell will provision an S3-compatible object storage
* **Note down these values** from your Object Storage settings:
  * `Endpoint` (e.g., `https://objstorage.leapcell.io`)
  * `Region` (e.g., `us-east-1`)
  * `Bucket Name` (e.g., `os-wsp1971045591851880448-xxxx-xxxx-xxxx`)
  * `Access Key ID` (e.g., `cf0742f423bd4c3f9932c54cb97315fb`)
  * `Secret Access Key` (e.g., `your-secret-key-here`)

### 4. Configure Environment Variables

* In your LeapCell project dashboard, go to the "Env Variables" section (left sidebar)
* Add the following environment variables using the "Add Env" button:

#### Required Variables:
* `DATABASE_URL`: Paste the PostgreSQL connection string from Step 2
* `SECRET_KEY`: Generate a strong secret key (use `uv run python oppman.py secrets` locally)
* `ENVIRONMENT`: Set to `production`
* `UPLOAD_DIR`: Set to `/tmp/uploads`

#### S3 Object Storage Variables:
* `S3_ACCESS_KEY`: Paste the Access Key ID from Step 3
* `S3_SECRET_KEY`: Paste the Secret Access Key from Step 3
* `S3_BUCKET`: Paste the Bucket Name from Step 3
* `S3_ENDPOINT_URL`: Paste the Endpoint from Step 3
* `S3_REGION`: Paste the Region from Step 3

#### Optional Variables:
* `OPENROUTER_API_KEY`: (Optional) Your OpenRouter API key for AI features

### 5. Deploy the Application

* Ensure all your code changes are committed and pushed to your GitHub repository
* In your LeapCell project dashboard, go to the "Deployments" section
* Trigger a new deployment
* Monitor the deployment logs for any errors

### 6. Initialize the Demo Data

* Once your application is deployed and running, find its public URL (e.g., `https://your-app.leapcell.dev/`)
* Open your terminal and run the following curl command to trigger the full demo initialization:
  ```bash
  curl -X POST https://your-app.leapcell.dev/async/init-demo
  ```
* Monitor your LeapCell project logs for the initialization progress

### 7. Verify Deployment

* Access your application's public URL in a web browser
* Navigate to `/webinar-registrants` to see if sample data and photos have been loaded
* Check the `/debug/database-data` endpoint to verify database tables are populated
* Test the health check endpoint: `https://your-app.leapcell.dev/kaithheathcheck`

### 8. Test S3 Object Storage (Optional)

* **Backup photos to S3**:
  ```bash
  curl -X POST https://your-app.leapcell.dev/admin/backup-files
  ```
* **Restore photos from S3**:
  ```bash
  curl -X POST https://your-app.leapcell.dev/admin/restore-files
  ```

## Troubleshooting

### Common Issues:

* **Database Connection Errors**: Check that `DATABASE_URL` is correctly formatted
* **S3 Backup/Restore Fails**: Verify all S3 environment variables are set correctly
* **Initialization Timeout**: Check deployment logs for database connection issues
* **File Upload Issues**: Ensure `UPLOAD_DIR` is set to `/tmp/uploads`

### Debug Endpoints:

* `/debug/connection` - Check database connectivity
* `/debug/database-data` - Verify database tables and data
* `/kaithheathcheck` - Basic health check

## Next Steps

* Customize the application for your specific needs
* Add your own data and content
* Explore the admin panel at `/admin/`
* Test the AI chat features (if `OPENROUTER_API_KEY` is configured)

## Support

* Check the main README.md for detailed documentation
* Review the DEPLOYMENT.md for additional deployment options
* Use the LeapCell dashboard logs for debugging
