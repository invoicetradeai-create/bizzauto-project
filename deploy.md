# Deployment Guide for Railway

This guide provides step-by-step instructions on how to deploy your **backend** application to Railway, including environment variable configuration.

## Step 1: Create a New Project from GitHub

1.  Log in to your [Railway account](https://railway.app/).
2.  On your dashboard, click the **+ New Project** button.
3.  Select **Deploy from GitHub repo**.
4.  Choose your `invoicetradeai-create/bizzauto-project` repository.

## Step 2: Add Your Databases (PostgreSQL and Redis)

Your application needs a PostgreSQL database and a Redis instance.

1.  After creating your project, you'll be taken to the project view. Click the **+ New** button.
2.  Select **Database** and then choose **PostgreSQL**.
3.  Click **+ New** again.
4.  Select **Database** and then choose **Redis**.

You will now have three services in your project: your backend (`bizzauto-project`), a PostgreSQL database, and a Redis instance.

## Step 3: Configure Your Backend Service

1.  Click on your backend service (named `bizzauto-project`).
2.  Go to the **Settings** tab.
3.  Under the **Build** section, set the **Root Directory** to `bizzauto_api`. Railway should automatically detect your `Dockerfile` at `/bizzauto_api/Dockerfile`.

## Step 4: Configure Environment Variables

This is the most important step for a successful deployment. Go to the **Variables** tab for your backend service (`bizzauto-project`) and add the following variables.

---

### ✅ Environment Variables to **ADD**:

*   **`DATABASE_URL`**:
    *   **How to get it**: Click the "Add Variable" button, and you will see a list of available variables from your other services. Select the `DATABASE_URL` from your PostgreSQL service. Railway automatically creates this connection string for you.
    *   **Example Value**: It will look something like `postgresql://postgres:password@some-host:port/railway`.

*   **`REDIS_URL`**:
    *   **How to get it**: Similar to the `DATABASE_URL`, select the `REDIS_URL` from your Redis service.
    *   **Example Value**: It will look something like `redis://default:password@some-host:port`.

*   **`SUPABASE_URL`**:
    *   **How to get it**: You get this from your Supabase project settings.
    *   **Example Value**: `https://your-project-id.supabase.co`

*   **`SUPABASE_KEY`**:
    *   **How to get it**: This is your Supabase **`service_role` key** (the secret one) from your Supabase project settings under "API".
    *   **Example Value**: A long, secret key that starts with `ey...`

*   **`GCS_BUCKET_NAME`**:
    *   **How to get it**: This is the globally unique name of the Google Cloud Storage bucket you created.
    *   **Example Value**: `your-bizzauto-uploads-bucket`

*   **`GOOGLE_APPLICATION_CREDENTIALS`**:
    *   **How to get it**: This is the **entire content** of the JSON key file you downloaded from your Google Cloud service account.
    *   **How to add it**: In Railway, when you add this variable, there's an option to open a special editor for multi-line values. Copy the full JSON content and paste it there.
    *   **Example Value**:
        ```json
        {
          "type": "service_account",
          "project_id": "your-gcp-project-id",
          "private_key_id": "...",
          "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
          "client_email": "...",
          "client_id": "...",
          "auth_uri": "...",
          "token_uri": "...",
          "auth_provider_x509_cert_url": "...",
          "client_x509_cert_url": "..."
        }
        ```

---

### ❌ Environment Variables to **AVOID** adding manually:

*   **`PORT`**: You don't need to set this. Your `Dockerfile` already "exposes" port 8000, and Railway automatically detects this and routes traffic to it.
*   **`POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`**: These are for the database *itself* and are used for local development with `docker-compose.yml`. In Railway, you only need the full `DATABASE_URL` connection string, which contains all this information.

---

## Step 5: Deploy

Once you have added all the environment variables, Railway will automatically trigger a new deployment. You can monitor the progress in the **Deployments** tab. If the deployment is successful, you will see a green checkmark, and your backend will be live at the public URL provided in the **Settings** tab.

---

## Deploying Your Frontend (Optional)

You can deploy your frontend (`bizz_autofinal_ui`) as a separate service within the same Railway project:

1.  **New Service**: Add a new service to your project and select your GitHub repository again.
2.  **Configure Frontend Service**: For this new service, go to its **Settings** tab.
    *   **Root Directory**: Set the "Root Directory" to `bizz_autofinal_ui`.
    *   **Build Method**: Ensure the "Build Method" is set to "Dockerfile".
3.  **Configure Environment Variables**: In the **Variables** tab for your frontend service, you'll need to add a `NEXT_PUBLIC_API_URL` variable. The value for this will be the public URL that Railway provides for your deployed backend service.
    *   **Example Value**: `https://bizzauto-project-production.up.railway.app` (replace with your actual backend URL).
4.  **Deploy**: Railway will then build and deploy your frontend service.
