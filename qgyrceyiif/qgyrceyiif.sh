#!/bin/bash
git_token=$1
branch="dev-test"  # branch (techzone/development)
github_url=https://github.com/ibm/ibmtechzone-assets
project_name=ibmtechzone-assets
username=IBM

if [[ $PLAYGROUND_ENVIRONMENT == *"development"* ]]; then
      branch="development" 
fi
if [[ $PLAYGROUND_ENVIRONMENT == *"techzone"* ]]; then
      branch="techzone" 
fi

rm -rf $project_name
if [ ! -d $project_name ]; then
    git clone --single-branch --branch $branch  $github_url 
fi

cd $project_name
git config user.email "demoframework@ibm.com"
git config user.name "demoframework"

directories=$(git ls-tree --name-only -d HEAD | cut -d/ -f1 | sort -u)

#loop through all the assets in git repo and update the timestamp
for dir in $directories; do
    if [[ $dir == *"meta-data"* ]]; then #to skip updating the meta-data folder
        continue
    fi
        readme_file="/Users/nupur/Desktop/allRepos/Developer-Playground/asset-hub-work/playground-unified-services/$project_name/$dir/readme.json"
        tmpfile="/Users/nupur/Desktop/allRepos/Developer-Playground/asset-hub-work/playground-unified-services/$project_name/$dir/temp_readme.json"
        # json_data=$(curl -s "https://api.github.com/repos/$username/$project_name/commits?path="$dir"&sha="$branch)
        json_data=$(curl --location --request GET "https://api.github.com/repos/$username/$project_name/commits?path="$dir"&sha="$branch --header "Authorization: Bearer "$git_token)

        timestamp=$(echo "$json_data" | jq -r '. | max_by(.commit.author.date) | .commit.author.date')
        # Convert the date to seconds since the Unix epoch and then multiply by 1000
        seconds=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$timestamp" "+%s")
        latest_commit_date=$((seconds * 1000))  
        # echo $latest_commit_date

        # Add the "timestamp" field to the readme json file
        jq --arg timestamp "$latest_commit_date" '. + {timestamp: $timestamp}' "$readme_file" > "$tmpfile"

        mv "$tmpfile" "$readme_file"
done

echo "Pushing asset to Public repository"
git add .
git commit -am "Updated the timestamp"
git push https://user_name:$git_token@github.com/$username/$project_name.git


if [ $? == 0 ]; then 
  echo "Successfully pushed Asset to Public Repository"
fi

if [ $? != 0 ]; then
  echo "Something went wrong with pushing asset to Public Repository"
fi

cd ..
# rm -rf $project_name
echo "success"