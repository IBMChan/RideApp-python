from enum import Enum
from abc import ABC, abstractmethod
import time

class UserRole(Enum):
    RIDER = "rider"
    DRIVER = "driver"
    

class AbstractUser(ABC):
    def __init__(self, user_id: str, name: str, email: str, phone: str, password: str, role: UserRole):
        self.user_id = user_id
        self.name = name
        self.email = email
        self._phone = phone
        self.password = password
        self.role = role
        self.created_at = int(time.time() * 1000)

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value: str):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be 10 digits")
        self._phone = value

    @abstractmethod
    def validate_user(self):
        """Each user type must implement validation"""
        pass


class Rider(AbstractUser):
    def validate_user(self):
        return True

    def __str__(self):
        return f"[RIDER] {self.name} ({self.email})"


class Driver(AbstractUser):
    def __init__(self, user_id: str, name: str, email: str, phone: str, password: str, license_number: str):
        super().__init__(user_id, name, email, phone, password, UserRole.DRIVER)
        self.license_number = license_number

    def validate_user(self):
        if not self.license_number:
            raise ValueError("Driver must have a license number")
        return True

    def __str__(self):
        return f"[DRIVER] {self.name} ({self.email}) | License: {self.license_number}"

# from enum import Enum
# import time

