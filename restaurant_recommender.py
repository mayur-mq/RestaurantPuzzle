import os
import csv
import sys
from collections import defaultdict

from errors import FileReadError


class RestaurantRecommender(object):
    def __init__(self, restaurant_file):
        self.restaurant_file = restaurant_file
        self.restaurant_items = self._prepare_restaurant_menu()

    def _check_file_validity(self):
        file_validity = (
            os.path.exists(self.restaurant_file) and 
            os.path.getsize(self.restaurant_file) > 0 and 
            os.path.splitext()[1] == ".csv")
        if not file_validity:
            raise FileReadError("Invalid input file.")

    def _prepare_restaurant_menu(self):
        '''
        It will prepare a restaurants map with all the available items. If
        mutiple entries are found then the item with minimum price will be 
        selected.
        '''
        # Map of resturant id to price list of items. e.g.,
        # {'1': {'item': 'burger', 'price': 12.4},
        # {'item': ['burger, pizza'], 'price': 34.2}], ..}
        rest_items = defaultdict(list)
        with open(self.restaurant_file, "rb") as f:
            seen_rows = set()
            reader = csv.reader(f)
            for row in reader:
                # Only consider unique row.
                try:
                    restaurant_id = int(row[0].strip())
                    price = float(row[1].strip())
                    item = tuple([r.strip().lower() for r in sorted(row[2:])])
                except IndexError:
                    continue
                item_row = (restaurant_id, price, item,)
                if not self.validate(restaurant_id, price, item):
                    print "Escaping Invalid rows : {}".format(item_row)
                    continue
                if item_row in seen_rows:
                    continue
                seen_rows.add(item_row)
                rest_items[restaurant_id].append(
                    {
                        'price': price,
                        'item': item
                    }
                )
        return rest_items

    def validate(self, rid, price, item_list):
        return (rid > 0 and price > 0.0 and item_list is not None)

    def recommend(self, menu_items):
        menu_items = [mi.lower().strip() for mi in menu_items]
        selected_restaurants = {}
        for restaurant_id, items_info in self.restaurant_items.items():
            # Split the meal and value_meal from all the items available in 
            # a restaurant.
            rest_price = 0.0
            menu_items_status = {item: False for item in menu_items}
            meals = {item_info['item'][0]: item_info['price'] 
                     for item_info in items_info 
                     if len(item_info['item']) == 1}
            value_meals = {item_info['item']: item_info['price'] 
                           for item_info in items_info 
                           if len(item_info['item']) > 1}
            menu_items = set(menu_items)
            selected_menu_items = {}
            select_val_meal_price = 0.0  
            min_price = 100000000000000000000.00
            for val_meal_items, val_meal_price in value_meals.items():
                possible_select_items = menu_items.intersection(val_meal_items)
                if len(possible_select_items) >= len(selected_menu_items):
                    if float(val_meal_price) < min_price:
                        selected_menu_items = possible_select_items
                        select_val_meal_price = val_meal_price

            try:
                select_val_meal_price_separate = sum(
                    [meals[item] for item in selected_menu_items])
                if select_val_meal_price_separate < select_val_meal_price:
                    select_val_meal_price = select_val_meal_price_separate
            except KeyError:
                pass

            menu_items_status.update(
                {item: True for item in selected_menu_items}
            )
            remaining_menu_items = menu_items.difference(selected_menu_items)

            rest_price += select_val_meal_price
            for rem_item in remaining_menu_items:
                if rem_item in meals:
                    rest_price += meals[rem_item]
                    menu_items_status[rem_item] = True
            if all(menu_items_status.values()):
                selected_restaurants[restaurant_id] = rest_price

        if not selected_restaurants:
            return "Nil"
        else:
            result = min(selected_restaurants.items(), key=lambda l: l[1])
            return "{} {}".format(result[0], result[1])


def main():
    if len(sys.argv) < 3:
        print 'Nil'
        return

    restaurant_items_file = sys.argv[1]
    menu_items = sys.argv[2:]

    rr = RestaurantRecommender(restaurant_items_file)
    print rr.recommend(menu_items)


if __name__ == "__main__":
    main()
