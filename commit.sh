# Commit script so I dont have to constantly rewrite the same commands

git add .
git commit -m "$1"
git pull --rebase origin main
git push origin
