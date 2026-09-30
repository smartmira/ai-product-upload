from gpt_classifier import classify_product
from get_attribute_values import get_attribute_values


product = "Professional watercolor brush set"

classification = classify_product(product)

print("\nCATEGORY")
print(classification)

brick = classification["brick"]

attributes = get_attribute_values(brick)

print("\nATTRIBUTES")
print(attributes)