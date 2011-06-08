# class to assemble the data to be returned

class DataMunger():
    @classmethod
    def get_required_data(self, result, format):
        if format == 'id':
            return {'id': result['asset_id']}
        elif format == 'short':
            return {
                'id': result['asset_id'],
                'object_type': result['object_type'],
                'title': result['title']
                }
        elif format == 'full':
            return result
        else:
            raise TypeError('the format of data returned can be "id", "short" or "full"')
