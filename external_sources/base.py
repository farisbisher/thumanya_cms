from abc import ABC, abstractmethod

class ExternalProgramSource(ABC):
    @abstractmethod
    def fetch_programs(self):
        """
        Fetch programs from the external source.
        Return a list of dictionaries in CMS standard format:
        {
            "title": str,
            "description": str,
            "category": str,
            "language": str,
            "duration": str,
            "publish_date": str,
            "media_type": str,
            "media_url": str,
            "thumbnail_url": str,
            "metadata": dict
        }
        """
        pass
