# class to assemble the data to be returned
import exceptions

class DataMunger():
    @classmethod
    def get_required_data(cls, result, output_format):
        if output_format == 'id':
            return {'id': result['asset_id']}
        elif output_format == 'short' or output_format == '':
            return {
                'id': result['asset_id'],
                'object_type': result['object_type'],
                'title': result['title']
                }
        elif output_format == 'full':
            return result
        else:
            raise DataMungerFormatException("the output_format of data returned can be 'id', 'short' or 'full'")

class DataMungerFormatException(exceptions.Exception):
    def __init__(self, error_text='Data format error'):
        self.error_text = error_text
        return
        
    def __str__(self):
        print self.error_text
