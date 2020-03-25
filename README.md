# apache-ws-setup-windows
Deploying python services on windows, most of the times proves to be tricky. Windows task scheduler is not a very reliable platform, mostly on part of restarting the service automatically. PM2 is another option, which on most parts, is quite reliable. But sometimes, it is not able restart the service automatically because of it's dependence on pm2 dump file. If somehow the dump file is corrupted, services won't resurrect.

In this tutorial, we'll set up a python app on battle tested apache webserver. The python app is a flask app and uses a virtual environment for the libraries.

### Prerequisites:
- Flask based python app
- Ready to activate virtual env
- Apache webserver(available in this repo)

### Setup

1. Unzip the Apache webserver. Place the unzipped <b>Apache24</b> folder in <b>C:/</b>. We can place the Apache24 folder anywhere in our system but then we'll have to change the configurations to point to the folder of our choice. <b>C:/Apache24 is the default configuration.</b> We'll denote this path now with <b>APACHE_HOME</b> (This is only for this tutorial. No need to set up any such env variable)

2. By default apache runs on port 80 for http. If port 80 is not available:
    - Go to APACHE_HOME/conf
    - Edit `httpd.conf`
    - Find line `Listen xx`. Change xx to a port of your choice. Save file and exit.
    - Let's call this port <b>PORT</b>
    - Please note that this is the port on which our python app will be available. We need not serve our python apps using waitress or any other library. For instance, there would not be any need for `serve(app, host=config.host, port=config.port)` in app.py
    
3. Test initial Apache setup: 
    - `cd APACHE_HOME\bin`
    - Execute `https.exe`
    - browse http://localhost:PORT -> Should get a response
    
4. Install as windows service:
    - Execute `httpd.exe -k install`
    - Check in services.msc for a service called <b>Apache24</b>
    
5. Install mod_wsgi:
    - Assuming the virtual env is setup and flask app is ready. Let's call this virtuial env <b>FLASK_VIRTUAL_ENV</b>
    - Open command prompt as administrator. Activate virtual environment FLASK_VIRTUAL_ENV
    - Execute `pip install mod_wsgi`. It is important to bind mod_wsgi to the python interpreter against which the application will run.
    - Execute `mod_wsgi-express module-config`
    - Copy the output of the above command and paste it in <b>APACHE_HOME/conf/httpd.conf</b>, at the very end of the file.
    - Save file and exit.
    - Close command prompt.
    
6. Set up python application:
    - Let us call the application root directory <b>APP_DIR</b>
    - Within APP_DIR, create a directory `index`
    - Within APP_DIR/index, create a file `web.wsgi`. This will act as an entry point, for mod_wsgi, to your application.
    - Contents of `web.wsgi`:
      ```
      activate_this = "FLASK_VIRTUAL_ENV/Scripts/activate_this.py"
      with open(activate_this) as file_:
        exec(file_.read(), dict(__file__=activate_this))
      import sys

      sys.path.insert(0, APP_DIR)
 
      from app import app as application
      ```
    - In the above code, `from app import app as application` assumes your flask root file is <b>app.py</b> and app.py has an object called <b>app</b> which the root flask application object.
    - Also, create a directory `logs` under APP_DIR for apache to log application specific logs.
    
7. Configure a Virtual Host for the Flask App:
    - In APACHE_HOME/conf/extra/httpd-vhosts.conf, add following configuration:
      ```
      <VirtualHost *:PORT>
      ServerAdmin [admin-name-here]
      ServerName  [server_name]
      WSGIApplicationGroup %{GLOBAL}
      DocumentRoot APP_DIR
      WSGIScriptAlias / APP_DIR/index/web.wsgi"
      <Directory APP_DIR/index>
              Require all granted
      </Directory>
      ErrorLog APP_DIR/logs/error.log
      CustomLog APP_DIR/logs/custom.log common
      </VirtualHost>
      ```
    - Important configurations are: 
        * ServerName : name of the VM/machine on which application is being deployed.
        * DocumentRoot : root directory of flask app
        * WSGIScriptAlias : first argument for this signifies the application specific domain name. In this case, it is root of the webserver e.g. http://server_name:PORT/abc.html
        * Directory : gateway to the application i.e. APP_DIR/index
        * Require all granted : allows all requests
8. Enable httpd.conf to read virtual host file:
    - In APACHE_HOME/conf/httpd.conf, find the line `Include conf/extra/httpd-vhosts.conf` and uncomment it.
9. Restart the apache service from service manager. The application should be accessible at http://server_name:PORT/application_url

### Some Common Issues:

1. Make sure the user, under which Apache is running, has permissions over application directory.
2. If the server doesn't starts from service manager, you can also run `httpd.exe` under APACHE_HOME/bin, directly from command line. It prints useful log messages in case of error.
3. Apache logs under APACHE_HOME/logs also can be used for debugging.
4. Can refer (this)[https://github.com/GrahamDumpleton/mod_wsgi#connecting-into-apache-installation] for more details on mod_wsgi.

