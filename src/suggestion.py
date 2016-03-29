import os
import tagging
import database


def get_suggestions(selected_files):

    tag_ids = tagging.get_all_tag_ids()
    print("suggestion start")
    recomm_ids = []
    recomms = []
    file_ids = []
    tag_quantities = []
    i = 0
    query_items = "SELECT pk_id FROM file"
    final_ids = []

    cursor = database.get_current_gallery("connection").cursor()
    cursor.execute(query_items)
    result = cursor.fetchall()

    for item in result:
        file_ids.append(item[0])

    for tag_id in tag_ids:
        tag_quantities.append([0, tag_id])

    for tempFile in file_ids:
        counter = 0
        for tag_id in tag_ids:
            if tagging.file_has_tag_id(tempFile, tag_id):
                tag_quantities[counter][0] += 1
            counter += 1

    if len(tag_ids) > 7:
        while i < 7:
            if not tag_quantities:
                break

            length = len(selected_files)
            tagcount = 0
            for selected_file in selected_files:
                if tagging.file_has_tag_id(selected_file, max(tag_quantities)[1]):
                    tagcount += 1

            if tagcount is length:
                tag_quantities.remove(max(tag_quantities))
                i += 1

            else:
                recomm_ids.append(max(tag_quantities)[1])
                tag_quantities.remove(max(tag_quantities))
                i += 1
        i = 0
    else:
        while i < len(tag_ids):
            if not tag_quantities:
                break

            length = len(selected_files)
            tagcount = 0
            for selected_file in selected_files:
                if tagging.file_has_tag_id(selected_file, max(tag_quantities)[1]):
                    tagcount += 1

            if tagcount is length:
                tag_quantities.remove(max(tag_quantities))
                i += 1

            else:
                recomm_ids.append(max(tag_quantities)[1])
                tag_quantities.remove(max(tag_quantities))
                i += 1
        i = 0

    tag_corr = []
    corr_recomm_ids = []

    for tag_id in tag_ids:
        tag_corr.append([0, tag_id])

    for tempFile in selected_files:
        counter = 0
        for tag_id in tag_ids:
            if tagging.file_has_tag_id(tempFile, tag_id):
                tag_corr[counter][0] += 1
            counter += 1

    if len(tag_ids) > 7:
        while i < 7:
            if not tag_corr:
                break

            if max(tag_corr)[0] < len(selected_files):
                corr_recomm_ids.append(max(tag_corr)[1])
                tag_corr.remove(max(tag_corr))
                i += 1

            else:
                tag_corr.remove(max(tag_corr))
                i += 1

        i = 0
    else:
        while i < len(tag_ids):
            if not tag_corr:
                break

            if max(tag_corr)[0] < len(selected_files):
                corr_recomm_ids.append(max(tag_corr)[1])
                tag_corr.remove(max(tag_corr))
                i += 1

            else:
                tag_corr.remove(max(tag_corr))
                i += 1

        i = 0

    if not selected_files:
        corr_recomm_ids.append(1)
        recomm_ids.append(1)

    corr = True
    recomm = True

    while True:
        if not recomm_ids and not corr_recomm_ids:
            break

        if len(selected_files) > 1:
            if corr_recomm_ids[i] not in final_ids and corr is True:
                final_ids.append(corr_recomm_ids[i])
                if corr_recomm_ids[i] is corr_recomm_ids[len(corr_recomm_ids)-1]:
                    corr = False

        if recomm_ids[i] not in final_ids and recomm is True:
            final_ids.append(recomm_ids[i])
            if corr_recomm_ids[i] is corr_recomm_ids[len(corr_recomm_ids)-1]:
                recomm = False

        if recomm_ids[i] is recomm_ids[len(recomm_ids)-1] and corr_recomm_ids[i] is corr_recomm_ids[len(corr_recomm_ids)-1]:
            break

        i += 1
    i = 0

    for tag in final_ids:
        recomms.append(tagging.tag_id_to_name(tag))

    return recomms

