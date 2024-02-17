def get_images_in_folder() -> list:
    folder = os.path.join(MEDIA_STATIC_PATH, "images")
    folder_list = []
    for a in os.listdir(folder):
        a = f"{folder}/{a}"
        folder_list.append(
            f"{a.split('/')[-4]}/{a.split('/')[-3]}/{a.split('/')[-2]}/{a.split('/')[-1]}"
        )
    return sorted(folder_list)

def get_videos_in_folder() -> list:
    folder = os.path.join(MEDIA_STATIC_PATH, "videos")
    folder_list = []
    for file in os.listdir(folder):
        file_dict = {}
        file = os.path.join(folder, file)
        metadata = ffmpeg.probe(file)["format"]["tags"]
        file_dict["file_path"] = "/".join(file.split("/")[1:])
        file_dict["title"] = metadata.get("title") or ""
        file_dict["original_start_time"] = metadata.get("comment") or ""
        file_dict["username"] = metadata.get("artist") or ""
        file_dict["show"] = metadata.get("show") or ""
        file_dict["episode_number"] = metadata.get("episode_id") or ""
        file_dict["season_number"] = metadata.get("season_number") or ""
        folder_list.append(file_dict)
    return folder_list

def delete_file(self, file_path) -> bool:
    try:
        os.remove(f"./app/{file_path}")
        return True
    except:
        return False