# Site Reliability Engineer Challenge

Welcome to the Site Reliability Engineer Challenge. Your task is to follow the Steps to Complete section below based on the code in this repository.

You should fork or clone this repository and publish to your own github account. This should be public if completing the github actions steps (you can make it private or remove after we have reviewed), or create a deploy key so we can clone the code if it is private.

If you are concerned that your current github account is linked to any current employment and you do not want this activity linked, then create a new github account.

If you do not have a github account, you can still complete this with GitLab, Codeberg, a self hosted Gitea instance or others, however do be aware that Thinkific uses Github and you should be familar with it.

You will supply to us after you are finished:
- The repository URL
- A deploykey if the repository is private

The idea is that we should be able to see: commit history; Github actions runs; the contents of the repository.

Notes:
- You are not expected to understand python, bugs in the application are not what you are trying to solve here.
- You don't have to complete everything, if you can't, at least leaving enough notes of next steps in a markdown document are helpful.
- Don't worry! Just try it!
- Nobody is perfect, if you have made mistakes and they show up in the commit history this looks better than a clean slate (but it is optional, feel free to fix your commit history if you like)
- If you run out of github actions credits for running workflows don't feel the need to pay, just make a note or leave comments on how you would implement if you cannot test the changes.

Things that aren't required but will be favourable:
- Commit history (small, frequent commits are better than large commits)
- Signed commits
- Pushed image to GHCR with a github actions build pipeline
- Build attestations for the docker image

# DumbKV

This is a KV server that you shouldn't use. It's only purpose is to create something that can be run. It doesn't store things well and doesn't do a lot of checks so it's very easy to DoS this. 

Keys are sha265 hashed, so you if you forget your key you will have to guess what it is again. The values are encrypted with the hashed key values.

# Running

Install uv by following https://docs.astral.sh/uv/getting-started/installation/

Install python 3.12
```
uv python install 3.12
```

Install dependencies:
```
uv sync
```

Create an `.env` file. by default using the sqlite storage:
```
DATABASE_LOCATION=dumbkv.db
DATABASE_TYPE=sqlite
```

Start server:
```
uv run uvicorn main:api --host 0.0.0.0 --port 8000 --log-config logging.yaml
```

Then load the basic UI at http://127.0.0.1:8000/ or open the swagger docs at http://127.0.0.1:8000/docs

# Postgres storage

To use the optional postgres storage, start a new postgres instance:
```
docker run -it --rm -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres
```

Then in your `.env` file set:
```
DATABASE_LOCATION=postgres://postgres:postgres@localhost/postgres
DATABASE_TYPE=postgres
```

# Running tests

Run pytest with:
```
uv run python -m pytest
```

By default this will use the an in memory sqlite backend. To test with postgres start pytest with the `--database-location` argument:
```
uv run python -m pytest -v --database-location=postgres://postgres:postgres@127.0.0.1/postgres
```


# Steps to complete

Feel free to check these boxes in your copy along the way. If you want to leave short notes about your changes you can add them to this list also.

## Build
- [ ] Finish the dockerfile to run this project
- [ ] Finish the github action to build the docker image (no need to push anywhere if you don't want to)

## Test
- [ ] Create a github actions workflow that runs the tests on each pull_request
- [ ] Create an additional test workflow that runs a postgres service and update the test config to use this postgres backend

## Create the kubernetes manifests to run this service

The manifests can be saved in a `manifests` directory.

- [ ] Create a deployment, including a health check, using the sqlite backend. We only need 1 replica, and we should prevent multiple instances from running
- [ ] Create a service
- [ ] Create a PVC and ensure the database directory is named `dumbkvstore`. The storage class name is `efs`
- [ ] Create an ingress or gateway for the hostname `dumbkv.example.com`, the service will be available on the root path, the cert-manager cluster issuer is named `letsencrypt`
- [ ] Update the kubernetes manifests to support the postgres backend

## Monitoring
- [ ] Create a service monitor objects for prometheus to scrape the metrics
- [ ] Create a markdown document describing what SLO you would set for this application