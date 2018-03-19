# gcloud_cli

Tracks changes in the gcloud CLI

```bash
gsutil ls -l gs://cloud-sdk-release/for_packagers/linux > list.txt

# get latest version number from https://cloud.google.com/sdk/downloads

gsutil cp gs://cloud-sdk-release/for_packagers/linux/google-cloud-sdk-tests_193.0.0.orig.tar.gz .
gsutil cp gs://cloud-sdk-release/for_packagers/linux/google-cloud-sdk_193.0.0.orig.tar.gz .

tar -xzf google-cloud-sdk_193.0.0.orig.tar.gz ;\
tar -xzf google-cloud-sdk-tests_193.0.0.orig.tar.gz
```
