from mimesis import Generic
from mimesis.enums import Gender
from mimesis.providers import Finance, Payment, Text
from faker import Faker
from typing import Dict, Any
import random

class DataGenerator:
    def __init__(self):
        """Initialize data generators."""
        # Initialize Mimesis with Indian locale
        self.generic = Generic('en')
        self.finance = Finance('en')
        self.payment = Payment('en')
        self.text = Text('en')
        
        # Initialize Faker with Indian locale
        self.faker = Faker(['en_IN'])

    def generate_customer_profile(self) -> Dict[str, Any]:
        """Generate a complete customer profile."""
        gender = random.choice([Gender.FEMALE, Gender.MALE])
        return {
            "name": self.generic.person.full_name(gender=gender),
            "gender": gender.name,
            "age": self.generic.person.age(minimum=18, maximum=80),
            "email": self.generic.person.email(),
            "phone": self.generic.person.telephone(),
            "address": self.generic.address.address(),
            "city": self.generic.address.city(),
            "state": self.generic.address.state(),
            "pan": self.faker.random_uppercase_letter() + self.faker.random_uppercase_letter() + 
                   self.faker.random_uppercase_letter() + "P" + self.faker.random_uppercase_letter() + 
                   str(self.faker.random_number(digits=4)) + self.faker.random_uppercase_letter(),
            "aadhaar": str(self.faker.random_number(digits=12)),
            "income": self.finance.price(minimum=10000, maximum=1000000),
            "occupation": self.generic.person.occupation(),
            "marital_status": self.generic.person.marital_status()
        }

    def generate_transaction(self, customer_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a transaction based on customer profile."""
        return {
            "amount": self.finance.price(minimum=100, maximum=1000000),
            "currency": "INR",
            "merchant": self.generic.business.company(),
            "category": self.generic.business.company_type(),
            "payment_method": self.payment.credit_card_number(),
            "timestamp": self.generic.datetime.timestamp(),
            "location": self.generic.address.city(),
            "customer_id": customer_profile["pan"],
            "customer_location": customer_profile["city"]
        }

    def generate_email_content(self, category: str) -> str:
        """Generate email content for different categories."""
        if category == "phishing":
            return self.text.text(quantity=5) + "\n\n" + \
                   self.text.text(quantity=3) + "\n\n" + \
                   "Please verify your account details by clicking here."
        elif category == "legitimate":
            return self.text.text(quantity=5) + "\n\n" + \
                   self.text.text(quantity=3) + "\n\n" + \
                   "Thank you for your business with us."
        return self.text.text(quantity=5)

    def generate_system_metrics(self) -> Dict[str, Any]:
        """Generate system metrics for cryptojacking simulation."""
        return {
            "cpu_usage": random.uniform(0, 100),
            "memory_usage": random.uniform(0, 100),
            "gpu_usage": random.uniform(0, 100),
            "processes": [
                self.generic.code.issn() for _ in range(random.randint(10, 20))
            ],
            "network_usage": random.uniform(0, 100)
        }
