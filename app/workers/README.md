## Important Notes on Redis Queues

> ### Mitigating no Hotreloading
>
> Make sure to re-run the container after making changes to the code. This is because the container is not running the code directly, but rather a copy of the code that was made when the container was built. This means that any changes made to the code will not be reflected in the container until it is rebuilt.
> Use the following command to rebuild the container:
>
> ```./run.sh```
>

> ### Viewing the Worker process logs
>
> 1. Open docker desktop
> 2. Click on the rq-worker container
> 3. Click on the files tab
> 4. Open the /tmp folder
> 5. Checkout the log file with the most recent change timestamp
>
