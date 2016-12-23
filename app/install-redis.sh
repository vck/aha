
cd ..

sudo rm /etc/nginx/sites-enabled/default
sudo cp nginx/kedaidesa-shortener /etc/nginx/sites-available/
su ln -S /etc/nginx/sites-available/kedaidesa-shortener /etc/nginx/sites-enabled/kedaidesa-shortener
sudo nginx -t
sudo service nginx restart
