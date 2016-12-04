from copy import deepcopy as dc


def db_store(db, fs_data_name_save_map=None):
    if fs_data_name_save_map is None:
        fs_data_name_save_map = {}

    def wrap(f):
        def wrapped_f(*args, **kwargs):
            gen = f(*args, **kwargs)
            for name, doc in gen:
                fs_doc = dc(doc)

                if name == 'descriptor':
                    # Mutate the doc here to handle filestore
                    for data_name in fs_data_name_save_map.keys():
                        fs_doc['data_keys'][data_name].update(
                            external='FILESTORE:')
                    fs_doc.update(
                        filled={k: False for k in fs_data_name_save_map.keys()}
                    )

                    doc.update(
                        filled={k: True for k in fs_data_name_save_map.keys()})

                elif name == 'event':
                    # Mutate the doc here to handle filestore
                    for data_name, sub_dict in fs_data_name_save_map.items():
                        fs_doc = sub_dict['saver'](data_name, fs_doc,
                                                   sub_dict['folder'], db.fs)

                # Always stash the (potentially) filestore mutated doc
                print(fs_doc)
                db.mds.insert(name, fs_doc)

                # Always yield the pristine doc
                yield name, doc

        return wrapped_f

    return wrap
