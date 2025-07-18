class FilterBuilder:
    
    def __init__(self):
        pass  
    
    @staticmethod
    def create_filter_dict(location_type, location, advanced_filters):
        if location_type == 'zipcode':
            location_filter = {'zipcode': {'$eq': int(location)}}
        elif location_type == 'address':
            location_filter = {'address': {'$eq': location}}
        else:
            location_filter = {'city': {'$eq': location}}

        clean_advanced_filters = {
            key: value for key, value in (advanced_filters or {}).items() if value is not None
        }

        return {**location_filter, **clean_advanced_filters}
