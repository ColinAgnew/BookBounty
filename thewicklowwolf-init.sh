#!/bin/sh

echo -e "\033[1;32mTheWicklowWolf\033[0m"
echo -e "\033[1;34mBookBounty\033[0m"
echo "Initializing app..."

cat << 'EOF'
_____________________________________

               .-'''''-.             
             .'         `.           
            :             :          
           :               :         
           :      _/|      :         
            :   =/_/      :          
             `._/ |     .'           
          (   /  ,|...-'             
           \_/^\/||__                
       _/~  `""~`"` \_               
     __/  -'/  `-._ `\_\__           
    /    /-'`  `\   \  \-.\          
_____________________________________
Brought to you by TheWicklowWolf   
_____________________________________

If you'd like to buy me a coffee:
https://buymeacoffee.com/thewicklow

EOF

PUID=${PUID:-1000}
PGID=${PGID:-1000}

echo "-----------------"
echo -e "\033[1mRunning with:\033[0m"
echo "PUID=${PUID}"
echo "PGID=${PGID}"
echo "-----------------"

# Create the required directories with the correct permissions
echo "Setting up directories.."
mkdir -p /bookbounty/downloads /bookbounty/config
chown -R ${PUID}:${PGID} /bookbounty

# Background process to fix permissions
(
  echo "Starting permission monitor..."
  while true; do
    find /bookbounty/downloads -type f -exec chmod 755 {} \; 2>/dev/null
    sleep 10
  done
) &

# Start the application with the specified user permissions
echo "Running BookBounty..."
exec su-exec ${PUID}:${PGID} gunicorn src.BookBounty:app -c gunicorn_config.py
