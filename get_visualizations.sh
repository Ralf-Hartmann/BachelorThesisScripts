#! /usr/bin/bash


d=20220713; 
while [ "$d" != 20230424 ]; do 

	# define cloudnet url
	cloudnet_url="https://cloudnet.fmi.fi/api/visualizations/?date=$(date -d "$d " '+%Y-%m-%d')&site=lindenberg&product=classification"
	
	
	echo "Querying cloundnet URL: $cloudnet_url"
	# get the filename of the image	
	image_id=$(curl $cloudnet_url | jq '.[]["visualizations"]' | jq -r '.[]["s3key"]')

	new_img_url=https://cloudnet.fmi.fi/api/download/image/${image_id}

	echo "New img url: ${new_img_url}"
	
	# download image
	curl -O $new_img_url
	
	#increment date
	d=$(date -d "$d + 1 day" '+%Y%m%d')
done
