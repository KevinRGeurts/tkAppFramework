"""
Defines a  class JSONArchivable, that can be mixed in with any class to provide JSON archiving (serialization and deserialization)
capabilities..

Concrete implementation child classes likely will:
    (1) Implement X() method for ...

Exported Classes:
    JSONArchivable -- mix-in class that provides JSON archiving capabilities.

Exported Exceptions:
    None    
 
Exported Functions:
    None
"""


# standard imports

# local imports


class JSONArchivable(object):
    """
    A class that can be mixed in with any class to provide JSON archiving (serialization and deserialization) capabilities.
    """
    def __init__(self):
        """
        Initialize the JSONArchivable mix-in.
         """
        pass

    def to_json_dict(self):
        """
        Convert the object to a JSON-serializable dictionary.
        Iterates through the attributes of the object, and adds those that are JSON-serializable (str, int, float, list, dict, bool) to the json_dict.
        If it encounters an attribute that is an instance of JSONArchivable, it calls that attribute's to_json_dict() method and adds the resulting dictionary to the json_dict.
        It skips attributes that are not JSON-serializable, and not JSONArchivable objects.
        :return: A JSON-serializable dictionary representing the object.
        """
        json_dict={}
        # Get a list of the names of attributes of the object.
        atrlst=dir(self)
        # Iterate the list of attribute names, get the attribute value for each name, and add it to the json_dict if it is JSON-serializable.
        for atr in atrlst:
            atrval=getattr(self,atr)
            if type(atrval) in [str, int, float, list, dict, bool]:
                json_dict[atr]=atrval
            elif isinstance(atrval, JSONArchivable):
                json_dict[atr]=atrval.to_json_dict()
            else:
                # Skip attributes that are not JSON-serializable, and not JSONArchivable objects.
                # Alternatively, could raise an exception here, or add some other handling for non-JSON-serializable attributes.
                pass
        return json_dict

    def from_json_dict(self, json_dict):
        """
        Update the object from a JSON-serializable dictionary. Must be implemented by subclasses to be useful, as otherwise will raise NotImplementedError if called.
        :parameter json_dict: A JSON-serializable dictionary representing the object.
        :return: None
        """
        # TODO: The code below is not quite right. Need to:
        # (1) iterate through the attibutes of self and get their type
        # (2) based on the type:
        # (3) Look the value up in the json_dict and set the attibute value based on the value in the dict,
        # (4) or call attribute.from_json_dict({correct part of json_dict})
        
        # Get a list of the names of attributes of the object.
        atrlst=dir(self)
        # Iterate the list of attribute names. Look for that name in the json_dict. If it is found,
        # get the attribute value for that name from the json_dict, and set the attribute of the object to that value.
        for atr in atrlst:
            archval = None
            try:
                archval = json_dict[atr]
            except KeyError:
                continue
            if type(archval) in [str, int, float, list, dict, bool]:
                self.setattr(self, atr, archval)
            elif isinstance(archval, JSONArchivable):
                # TODO: Need to extract a part of the parameter json_dict that is relevant to the JSONArchivable attribute, and pass that to the
                # from_json_dict() method of the JSONArchivable attribute. This will likely require some convention for how to structure the json_dict.
                archval.from_json_dict(json_dict)
            else:
                # Skip attributes that are not JSON-serializable, and not JSONArchivable objects.
                # Alternatively, could raise an exception here, or add some other handling for non-JSON-serializable attributes.
                pass
        return None


