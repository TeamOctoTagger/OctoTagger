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
    tag_quant_temp = []
    no_append = False
    i = 0
    counter = 0
    contains_tag = False
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

    for tag_id in tag_ids:
        tag_quant_temp.append([0, tag_id])

    for tempFile in selected_files:
        counter = 0
        for tag_id in tag_ids:
            if tagging.file_has_tag_id(tempFile, tag_id):
                tag_quant_temp[counter][0] += 1
            counter += 1

    if len(tag_ids) > 7:
        while i < 7:
            if not tag_quantities:
                break

            if max(tag_quant_temp)[0] < len(selected_files):
                recomm_ids.append(max(tag_quantities)[1])
                tag_quantities.remove(max(tag_quantities))
                tag_quant_temp.remove(max(tag_quant_temp))
                i += 1

            else:
                tag_quantities.remove(max(tag_quantities))
                tag_quant_temp.remove(max(tag_quant_temp))
                i += 1
        i = 0
    else:
        while i < len(tag_ids):
            if not tag_quantities:
                break

            if max(tag_quant_temp)[0] < len(selected_files):
                recomm_ids.append(max(tag_quantities)[1])
                tag_quantities.remove(max(tag_quantities))
                tag_quant_temp.remove(max(tag_quant_temp))
                i += 1

            else:
                tag_quantities.remove(max(tag_quantities))
                tag_quant_temp.remove(max(tag_quant_temp))
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

    while True:
        if not recomm_ids and not corr_recomm_ids:
            break

        if corr_recomm_ids[i] not in final_ids:
            final_ids.append(corr_recomm_ids[i])

        if recomm_ids[i] not in final_ids:
            final_ids.append(recomm_ids[i])

        if recomm_ids[i] is recomm_ids[len(recomm_ids)-1]:
            break

        if corr_recomm_ids[i] is corr_recomm_ids[len(corr_recomm_ids)-1]:
            break

        i += 1
    i = 0

    for tag in final_ids:
        recomms.append(tagging.tag_id_to_name(tag))

    print corr_recomm_ids
    print recomm_ids
    return recomms

