import pandas as pd
import os
from datetime import datetime


def create_numbered_groups(input_file, output_file):
    """
    Create numbered group format:
    1. Group by column A; duplicate rows show blank in column A
    2. Replace values in column A with sequential numbers (1, 2, 3, ...)
    3. Preserve original order and other column data
    """

    print("=" * 60)
    print("Excel BICYCLE Grouping & Formatting Tool")
    print("Effect: Column A labeled as BICYCLE_1, BICYCLE_2... forming clear groups")
    print("=" * 60)

    # Check file
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return False

    print(f"📁 Input file: {input_file}")
    file_size = os.path.getsize(input_file) / (1024 * 1024)
    print(f"📊 File size: {file_size:.2f} MB")
    print(f"💾 Output file: {output_file}")
    print("-" * 60)

    try:
        # Step 1: Read data
        print("⏳ Step 1: Reading Excel file...")
        start_time = datetime.now()

        df = pd.read_excel(input_file)

        read_time = (datetime.now() - start_time).total_seconds()
        print(f"✅ Reading complete! Time taken: {read_time:.1f} seconds")

        rows, cols = df.shape
        print(f"📈 Data shape: {rows:,} rows × {cols} columns")

        if rows == 0:
            print("❌ No data found in file")
            return False

        # Step 2: Analyze original column A
        first_col = df.columns[0]
        original_col_name = first_col
        print(f"\n⏳ Step 2: Analyzing column '{first_col}'...")

        # Count unique values
        unique_values = df[first_col].drop_duplicates(keep='first').tolist()
        unique_count = len(unique_values)

        print(f"📊 Column stats:")
        print(f"   - Unique values: {unique_count:,}")
        print(f"   - Will be numbered from BICYCLE_1 to BICYCLE_{unique_count}")

        # Show preview mapping
        print(f"🔄 Mapping preview:")
        preview_count = min(5, unique_count)
        for i in range(preview_count):
            original_val = str(unique_values[i])
            display_val = original_val[:15] + '...' if len(original_val) > 15 else original_val
            print(f"   {i + 1}. '{display_val}' → BICYCLE_{i + 1}")
        if unique_count > preview_count:
            print(f"   ... and {unique_count - preview_count} more")

        # Step 3: Create mapping
        print(f"\n⏳ Step 3: Creating mapping dictionary...")

        value_to_bicycle = {original_value: f"BICYCLE_{i + 1}" for i, original_value in enumerate(unique_values)}

        print(f"✅ Mapping created: {len(value_to_bicycle)} entries")

        # Step 4: Apply numbered grouping format
        print(f"⏳ Step 4: Applying BICYCLE group format...")

        df_result = df.copy()

        # Replace A column values with mapped BICYCLE_xx
        df_result[first_col] = df_result[first_col].map(value_to_bicycle)

        # Make duplicate rows blank (group effect)
        mask = df[first_col].duplicated(keep='first')
        df_result.loc[mask, first_col] = ''

        numbered_rows = (~mask).sum()
        blank_rows = mask.sum()

        print(f"✅ Formatting complete!")
        print(f"   - Numbered rows: {numbered_rows:,}")
        print(f"   - Blank rows: {blank_rows:,}")

        # Step 5: Validate data integrity
        print(f"\n⏳ Step 5: Validating data integrity...")

        result_rows, result_cols = df_result.shape
        if result_rows != rows or result_cols != cols:
            print(f"❌ Data structure mismatch! Original: {rows}×{cols}, Result: {result_rows}×{result_cols}")
            return False

        print(f"✅ Validation passed")
        print(f"   - Rows preserved: {rows:,}")
        print(f"   - Columns preserved: {cols}")
        print(f"   - Order preserved: same as original")

        # Step 6: Save results
        print(f"\n⏳ Step 6: Saving grouped Excel file...")
        save_start = datetime.now()

        df_result.to_excel(output_file, index=False)

        save_time = (datetime.now() - save_start).total_seconds()
        print(f"✅ File saved! Time taken: {save_time:.1f} seconds")

        # Step 7: Create mapping file
        mapping_file = output_file.replace('.xlsx', '_mapping.xlsx')
        print(f"\n⏳ Step 7: Creating mapping table...")

        mapping_df = pd.DataFrame({
            'BICYCLE_Number': [f"BICYCLE_{i}" for i in range(1, unique_count + 1)],
            'Original_Value': unique_values
        })
        mapping_df.to_excel(mapping_file, index=False)

        print(f"✅ Mapping file saved: {mapping_file}")

        # Summary
        total_time = (datetime.now() - start_time).total_seconds()

        print("\n" + "=" * 60)
        print("🎉 Numbered grouping format completed!")
        print("=" * 60)
        print(f"📊 Summary:")
        print(f"   Total rows: {rows:,} (unchanged)")
        print(f"   Total columns: {cols} (unchanged)")
        print(f"   Groups: {unique_count:,} (BICYCLE_1 to BICYCLE_{unique_count})")
        print(f"   Numbered rows: {numbered_rows:,}")
        print(f"   Blank rows: {blank_rows:,}")
        print(f"⏱️  Total time: {total_time:.1f} seconds")

        # File info
        if os.path.exists(output_file):
            output_size = os.path.getsize(output_file) / (1024 * 1024)
            print(f"\n💾 Output files:")
            print(f"   Main file: {output_file}")
            print(f"   Size: {output_size:.2f} MB")

        if os.path.exists(mapping_file):
            mapping_size = os.path.getsize(mapping_file) / 1024
            print(f"   Mapping file: {mapping_file}")
            print(f"   Size: {mapping_size:.1f} KB")

        # Preview
        print(f"\n🎯 Preview:")
        print(f"Column A ({original_col_name})  Column B      Column C      ...")
        print(f"1                       data1        info1        ...")
        print(f"                        data2        info2        ...")
        print(f"                        data3        info3        ...")
        print(f"2                       data4        info4        ...")
        print(f"                        data5        info5        ...")

        return True

    except Exception as e:
        print(f"❌ Processing failed: {str(e)}")
        import traceback
        print("\n🔍 Detailed error:")
        print(traceback.format_exc())
        return False


def main():
    print("🐍 Excel BICYCLE Grouping & Formatting Tool")
    print("Function: Number column A as BICYCLE_1, BICYCLE_2... and leave duplicates blank for clear grouping")
    print("-" * 60)

    print("🎯 Formatting Example:\n")
    print("Original Data:")
    print("  Column A         Column B     Column C")
    print("  efdf62549        data1        info1")
    print("  efdf62549        data2        info2")
    print("  efdf62549        data3        info3")
    print("  abc12345         data4        info4")
    print("  abc12345         data5        info5\n")
    print("After BICYCLE Grouping:")
    print("  Column A(BICYCLE)     Column B     Column C")
    print("  BICYCLE_1             data1        info1")
    print("                        data2        info2  ← blank for duplicates")
    print("                        data3        info3  ← blank for duplicates")
    print("  BICYCLE_2             data4        info4")
    print("                        data5        info5  ← blank for duplicates\n")
    print("✅ Advantages: clear grouping by BICYCLE number")
    print("📋 Includes: mapping table between BICYCLE numbers and original values")

    # File input
    print("\n" + "=" * 60)
    while True:
        print("📂 Please enter Excel file path:")
        print("   Tip: You can drag and drop the file into this window")
        input_path = input("Path: ").strip().strip('"')

        if not input_path:
            print("❌ Path cannot be empty")
            continue

        if not os.path.exists(input_path):
            print(f"❌ File not found: {input_path}")
            continue

        break

    # Generate output path
    base_name, ext = os.path.splitext(input_path)
    default_output = f"{base_name}_BICYCLE_grouped.xlsx"

    print(f"\n💾 Output file:")
    print(f"Default: {default_output}")
    custom_output = input("Custom path (press Enter to use default): ").strip().strip('"')

    output_path = custom_output if custom_output else default_output

    # Confirmation
    print(f"\n📋 Confirmation:")
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print(f"Effect: Column A becomes BICYCLE_1, BICYCLE_2... with grouped display")
    print(f"Additional: generates a mapping table for reference")

    confirm = input(f"\n🚀 Start processing? (Press Enter to confirm / n to cancel): ").lower()
    if confirm == 'n':
        print("❌ Cancelled by user")
        return

    # Execute
    success = create_numbered_groups(input_path, output_path)

    if success:
        print(f"\n🎉 Grouping completed!")
        print(f"✅ Column A renamed as 1, 2, 3... sequence")
        print(f"✅ Clear group visualization created")
        print(f"✅ All other columns preserved")
        print(f"✅ Mapping table generated")
        print(f"📁 Check the output files")
        print(f"\n💡 Tip: Use the mapping table to trace original values")
    else:
        print(f"\n❌ Processing failed")

    input(f"\nPress Enter to exit...")


if __name__ == "__main__":
    main()
