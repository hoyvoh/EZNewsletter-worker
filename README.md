# EZGROUP NEWSLETTER API
See API document at: [newsletters](https://newsletters.ezgroups.com.vn/docs/)
See detailed development and deployment structure here: [presentation](https://www.canva.com/design/DAGXK_QCTkU/yNCPFA02dd0RLyQqiL2Jgw/edit?utm_content=DAGXK_QCTkU&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)

This API is a scheduled task distribution module, dedicated to send emails periodically to subscriber based on newest posts and notifications from the blog module.

This is a part of a bigger web project containing:

- Frontend: [FrontEnd](https://github.com/Thupha41/EZLIFE-Real-Estate-Frontend) by Ngo Thuan Phat (@thupha41)
- SSO service: [SSO service](https://github.com/Thupha41/EZLIFE-Real-Estate-SSO-Backend) by Ngo Thuan Phat (@thupha41)
- Newsletter service: [Newsletter](https://github.com/hoyvoh/EZNewsletter-worker) by Ho Vy (@hoyvoh)
- API service: [API](https://github.com/hoyvoh/EZGROUP/tree/FR9/Detach-Subscibe-app) by Ho Vy (@hoyvoh)

Keywords: FastAPI, Redis, Celery, Docker-compose, EC2 deployment

## How to run after git clone

### Step 1: Establish .env file

Take a look at api/api/settings.py to see necessary environment variables to set up.

```
cat <<EOF > .env
>ENVAR=''
>...
>EOF
```

## Step 2: Start docker

But firstly, you must make sure your Docker is running. If you are on Ubuntu like me, check out: [Docker for ubuntu](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04)

Then, as you are ready:

```
cd EZLIFE/api
docker-compose up --build
```

Now you can access the API documents at 0.0.0.0:8000/api/docs/ to explore more further.

## Step 3: Stop docker

When you are done, make sure you have your containers cleaned up.

```
docker-compose down
docker system prune # (this is if you want a deep clean)
```
