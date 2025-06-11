# Juice Shop Terraform Deployment

This project uses Terraform to deploy and destroy an instance of [OWASP Juice Shop](https://owasp.org/www-project-juice-shop/) on AWS.  
GitHub Actions workflows automate the deployment and teardown.

---

## Prerequisites

### AWS Resources

- **S3 Bucket:** Used for storing the Terraform state file.
- **IAM User:** With programmatic access and permissions for EC2, VPC, S3, and (optionally) DynamoDB for state locking.

### GitHub Repository Secrets

- `AWS_ACCESS_KEY_ID`: Your IAM user's access key.
- `AWS_SECRET_ACCESS_KEY`: Your IAM user's secret key.

---

## Setup

### 1. Create an S3 Bucket

Create an S3 bucket (replace with your unique name):

```bash
aws s3api create-bucket --bucket your-unique-juice-shop-tfstate --region us-east-1
aws s3api put-bucket-versioning --bucket your-unique-juice-shop-tfstate --versioning-configuration Status=Enabled
```

### 2. (Optional) Create a DynamoDB Table for State Locking

```bash
aws dynamodb create-table \
  --table-name juice-shop-tf-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

### 3. Create an IAM User

- Go to AWS IAM → Users → Add user.
- Enable **Programmatic access**.
- Attach the following policies (or equivalent custom policy):
  - `AmazonEC2FullAccess`
  - `AmazonS3FullAccess` (or limited to your bucket)
  - `AmazonDynamoDBFullAccess` (if using state locking)
- Save the **Access Key ID** and **Secret Access Key**.

### 4. Add GitHub Repository Secrets

In your GitHub repo, go to **Settings → Secrets and variables → Actions** and add:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

---

## Configure Terraform Backend

In `main.tf`, ensure you have:

```hcl
terraform {
  backend "s3" {
    bucket = "your-unique-juice-shop-tfstate"
    key    = "juice-shop/terraform.tfstate"
    region = "us-east-1"
    # Uncomment if using DynamoDB for locking:
    # dynamodb_table = "juice-shop-tf-lock"
  }
}
```

---

## Running the Workflows

### Deploy

1. Go to **Actions** tab in your GitHub repo.
2. Select **Deploy Juice Shop** workflow.
3. Click **Run workflow**.

This will:
- Initialize Terraform with the S3 backend.
- Deploy the infrastructure.
- Output the public DNS of the Juice Shop instance.

### Destroy

1. Go to **Actions** tab.
2. Select **Destroy Juice Shop** workflow.
3. Click **Run workflow**.

This will:
- Use the same S3 state.
- Destroy all resources created by Terraform.

---

## Notes

- The workflows are defined in `.github/workflows/deploy.yml` and `.github/workflows/destroy.yml`.
- All AWS resources are managed via Terraform; manual changes may cause drift.
- Make sure your IAM user has access to the S3 bucket and (if used) DynamoDB table.

---

## Troubleshooting

- **State not found:** Ensure the S3 bucket and key are correct and accessible.
- **No resources to destroy:** Likely the state file is missing or not shared (check S3 backend config).
- **Permission errors:** Check IAM user permissions and GitHub secrets.

---

## Cleanup

To avoid AWS charges, always run the **Destroy Juice Shop** workflow when finished.

---
