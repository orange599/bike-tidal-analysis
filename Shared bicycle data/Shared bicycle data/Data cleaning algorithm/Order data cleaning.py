import pandas as pd
import os
from datetime import datetime


def clean_bicycle_data_preserve_order(input_file, output_file):
    """
    Clean bicycle data while preserving the original order.
    1. Record the original position of each row
    2. Judge line by line whether to keep it in original order
    3. Preserve the original report format
    """

    print("=" * 60)
    print("Bicycle Data Cleaning Tool - Order Preserved Version")
    print("Strictly preserving original order and format")
    print("=" * 60)

    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return False

    try:
        # Read data
        print("⏳ Reading data...")
        df = pd.read_excel(input_file)
        original_rows = len(df)

        print(f"📈 Original data: {original_rows:,} rows")

        # Identify columns
        bicycle_col = df.columns[0]
        status_col = df.columns[3]
        date_col = df.columns[4]
        time_col = df.columns[5]

        # Process time
        print("⏳ Processing time data...")
        df['FullTime'] = pd.to_datetime(df[date_col].astype(str) + ' ' + df[time_col].astype(str))

        # Fill missing BICYCLE_IDs and record original index
        df[bicycle_col] = df[bicycle_col].fillna(method='ffill')
        df['OriginalIndex'] = range(len(df))

        # Analyze which rows should be kept per bicycle
        print(f"\n⏳ Analyzing data anomalies...")

        valid_row_indices = set()  # Original indices to keep
        orders_info = {}  # Duration info for each order

        bicycles = df[bicycle_col].unique()
        total_orders = 0
        total_deleted = 0

        for bicycle_id in bicycles:
            bike_data = df[df[bicycle_col] == bicycle_id].copy().reset_index(drop=True)
            print(f"\n🔍 Analyzing {bicycle_id} ({len(bike_data)} rows)...")

            # Show status sequence
            status_sequence = bike_data[status_col].tolist()
            print(f"   Status sequence: {status_sequence}")

            # Determine which rows to keep and record order info
            keep_indices, bike_orders, bike_deleted = analyze_bicycle_data(bike_data, status_col, bicycle_id)

            # Convert back to original DataFrame indices
            original_indices = bike_data.iloc[keep_indices]['OriginalIndex'].tolist() if keep_indices else []
            valid_row_indices.update(original_indices)

            # Record order duration info
            for order in bike_orders:
                original_unlock_idx = bike_data.iloc[order['unlock_idx']]['OriginalIndex']
                original_lock_idx = bike_data.iloc[order['lock_idx']]['OriginalIndex']
                orders_info[original_unlock_idx] = order['duration']
                orders_info[original_lock_idx] = order['duration']

            print(f"   Result: {len(bike_orders)} orders, {len(keep_indices)} rows kept, {bike_deleted} rows deleted")
            total_orders += len(bike_orders)
            total_deleted += bike_deleted

        # Filter data by original order
        print(f"\n⏳ Filtering data by original order...")

        df_final = df[df['OriginalIndex'].isin(valid_row_indices)].copy()

        # Add duration column
        df_final['RideDuration_sec'] = ''
        for idx, row in df_final.iterrows():
            original_idx = row['OriginalIndex']
            # Add duration only for lock rows (status=1)
            if original_idx in orders_info and row[status_col] == 1:
                df_final.loc[idx, 'RideDuration_sec'] = orders_info[original_idx]

        # Apply original report format: show bicycle name only for first row of each
        print("⏳ Applying original report format...")
        prev_bicycle = None
        for idx, row in df_final.iterrows():
            current_bicycle = row[bicycle_col]
            if current_bicycle == prev_bicycle:
                df_final.loc[idx, bicycle_col] = ''
            else:
                prev_bicycle = current_bicycle

        # Remove temp columns, keep first 6 + duration
        original_columns = df.columns[:6].tolist()
        df_final = df_final[original_columns + ['RideDuration_sec']]

        final_rows = len(df_final)

        print(f"\n📊 Cleaning Results:")
        print(f"   Original rows: {original_rows:,}")
        print(f"   Final rows: {final_rows:,}")
        print(f"   Deleted rows: {total_deleted:,}")
        print(f"   Valid orders: {total_orders}")
        print(f"   Retention rate: {final_rows / original_rows * 100:.1f}%")

        # Save result
        print(f"\n⏳ Saving results...")
        df_final.to_excel(output_file, index=False)

        print(f"✅ Saved: {output_file}")

        # Show preview
        print(f"\n🎯 Preview (first 10 rows):")
        sample = df_final.head(10)
        for idx, row in sample.iterrows():
            bicycle = row.iloc[0] if row.iloc[0] != '' else '(blank)'
            status = row.iloc[3]
            time1 = row.iloc[4]
            time2 = row.iloc[5]
            duration = row.iloc[6]
            print(f"   {bicycle:<12} | Status={status} | {time1} {time2} | Duration={duration}")

        return True

    except Exception as e:
        print(f"❌ Processing failed: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False


def analyze_bicycle_data(bike_data, status_col, bicycle_id):
    """
    Analyze a single bicycle's data and return the indices to keep and order info.
    Does not modify data.
    """

    # Detect consecutive unlock anomalies
    rows_to_delete = set()
    for i in range(len(bike_data) - 1):
        if bike_data.iloc[i][status_col] == 0 and bike_data.iloc[i + 1][status_col] == 0:
            rows_to_delete.add(i)
            print(f"   ❌ Consecutive unlocks: delete row {i}")

    # Create temporary view without consecutive unlocks
    temp_indices = [i for i in range(len(bike_data)) if i not in rows_to_delete]
    if not temp_indices:
        return [], [], len(bike_data)

    # Find complete orders
    final_keep_indices = []
    orders = []

    i = 0
    while i < len(temp_indices):
        actual_idx = temp_indices[i]

        if bike_data.iloc[actual_idx][status_col] == 0:  # unlock
            unlock_idx = actual_idx
            unlock_time = bike_data.iloc[actual_idx]['FullTime']

            # Find matching lock
            lock_idx = None
            for j in range(i + 1, len(temp_indices)):
                check_idx = temp_indices[j]
                if bike_data.iloc[check_idx][status_col] == 1:
                    lock_idx = check_idx
                    lock_time = bike_data.iloc[check_idx]['FullTime']
                    break

            if lock_idx is not None:
                duration_seconds = (lock_time - unlock_time).total_seconds()

                if 1 <= duration_seconds <= 24 * 3600:
                    orders.append({
                        'unlock_idx': unlock_idx,
                        'lock_idx': lock_idx,
                        'duration': int(duration_seconds)
                    })

                    final_keep_indices.extend([unlock_idx, lock_idx])

                    print(
                        f"   ✅ Order {len(orders)}: rows {unlock_idx}-{lock_idx}, "
                        f"{unlock_time.strftime('%H:%M:%S')}→{lock_time.strftime('%H:%M:%S')}, "
                        f"{int(duration_seconds)} sec")

                    i = temp_indices.index(lock_idx) + 1
                else:
                    print(f"   ❌ Abnormal duration: {duration_seconds:.0f} sec")
                    i += 1
            else:
                print(f"   ❌ Isolated unlock: delete row {unlock_idx}")
                i += 1
        elif bike_data.iloc[actual_idx][status_col] == 1:
            print(f"   ❌ Isolated lock: delete row {actual_idx}")
            i += 1
        else:
            i += 1

    deleted_count = len(bike_data) - len(final_keep_indices)
    return final_keep_indices, orders, deleted_count


def main():
    print("🐍 Bicycle Data Cleaning Tool - Order Preserved Version")
    print("Strictly preserving original data order and report format")
    print("-" * 60)

    print("🎯 Features:")
    print("1. Preserve original data order")
    print("2. Preserve report format (first row shows bicycle name)")
    print("3. Remove consecutive unlocks and isolated records")
    print("4. Calculate ride duration")

    while True:
        print(f"\n📂 Please enter the Excel file path:")
        input_path = input("Path: ").strip().strip('"')

        if input_path and os.path.exists(input_path):
            break
        print("❌ File not found, please re-enter")

        # Avoid infinite loop if user keeps failing
    base_name = os.path.splitext(input_path)[0]
    output_path = f"{base_name}_order_preserved_cleaned.xlsx"

    print(f"\n💾 Output file: {output_path}")

    success = clean_bicycle_data_preserve_order(input_path, output_path)

    if success:
        print(f"\n🎉 Cleaning completed!")
        print(f"✅ Original order preserved")
        print(f"✅ Report format preserved")
        print(f"✅ Data cleaned and duration calculated")
    else:
        print(f"\n❌ Processing failed")

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
