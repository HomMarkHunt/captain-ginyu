import boto3

from wand.image import Image


def resize(event, context):
    print("function started.")
    print(event)
    try:
        client = boto3.client("s3")

        # originalチラシをec2上にダウンロード
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        key = event["Records"][0]["s3"]["object"]["key"]
        print("get s3 obj. key name = " + key)
        client.get_object(Bucket=bucket, Key=key)
        # lambdaは/tmpのみ読み書きの権限がある
        file_path = '/tmp/' + key
        client.download_file(bucket, key, file_path)

        # アップロード先のs3にあるファイルを全削除
        response = client.list_objects(Bucket='tirashi-resize')
        if 'Contents' in response:
            keys = [content['Key'] for content in response['Contents']]
            for key in keys:
                print("deleted file. key: " + key)
                client.delete_object(Bucket='tirashi-resize', Key='key')

        # メイン画像
        print("--start create main image : " + file_path)
        main_image = Image(filename=file_path)
        main_image.format = "jpg"
        main_image.resize(int(1024), int(900))
        main_resize_key = file_path.replace(".pdf", "_main_resize.jpg")
        main_image.save(filename=main_resize_key)
        client.upload_file(main_resize_key, "tirashi-resize", main_resize_key[5:], ExtraArgs={'ACL': 'public-read'})
        print("--uploaded main image--")

        # さぶ画像
        print("--start create sub image : " + file_path)
        sub_image = Image(filename=file_path)
        sub_image.format = "jpg"
        sub_image.resize(int(240), int(200))
        sub_resize_key = file_path.replace(".pdf", "_sub_resize.jpg")
        sub_image.save(filename=sub_resize_key)
        client.upload_file(sub_resize_key, "tirashi-resize", sub_resize_key[5:], ExtraArgs={'ACL': 'public-read'})
        print("--uploaded sub image--")

        print("function finished.")

    except Exception as e:
        print(e)
