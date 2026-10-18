import argparse
import pandas as pd
from math import sqrt

def read_star(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        optics_section = []
        particles_section = []
        read_optics = False
        read_particles = False
        for line in lines:
            if line.startswith('data_optics'):
                read_optics = True
                read_particles = False
            elif line.startswith('data_particles'):
                read_particles = True
                read_optics = False
            elif read_optics:
                optics_section.append(line)
            elif read_particles:
                particles_section.append(line)

        def parse_section(section):
            header_end_idx = None
            for idx, line in enumerate(section):
                if line.startswith('_rln'):
                    header_end_idx = idx
            header = section[:header_end_idx+1]
            data = section[header_end_idx+1:]
            data = [line.split() for line in data if line.strip()]
            columns = [line.split()[0] for line in header if line.startswith('_rln')]
            df = pd.DataFrame(data, columns=columns)
            
            if '_rlnCoordinateX' in df.columns and '_rlnCoordinateY' in df.columns:
                df['_rlnCoordinateX'] = df['_rlnCoordinateX'].astype(float)
                df['_rlnCoordinateY'] = df['_rlnCoordinateY'].astype(float)
            
            return header, df
        
        optics_header, optics_df = parse_section(optics_section)
        particles_header, particles_df = parse_section(particles_section)

        return optics_header, optics_df, particles_header, particles_df

def write_star(optics_header, optics_df, particles_header, particles_df, file_path):
    with open(file_path, 'w') as f:
        f.writelines(optics_header)
        optics_df.to_csv(f, sep=' ', index=False, header=False)
        f.writelines(particles_header)
        particles_df.to_csv(f, sep=' ', index=False, header=False)

def distance(x1, y1, x2, y2):
    return sqrt((x1 - x2)**2 + (y1 - y2)**2)

def main():
    parser = argparse.ArgumentParser(description='Compare particle coordinates in two RELION star files.')
    parser.add_argument('--star1', required=True, help='Path to the first star file')
    parser.add_argument('--star2', required=True, help='Path to the second star file')
    parser.add_argument('--radius', type=float, required=True, help='Radius for coordinate comparison')

    args = parser.parse_args()

    optics_header1, df1, particles_header1, particles_df1 = read_star(args.star1)
    optics_header2, df2, particles_header2, particles_df2 = read_star(args.star2)

    grouped_df1 = particles_df1.groupby('_rlnMicrographName')
    grouped_df2 = particles_df2.groupby('_rlnMicrographName')

    only_in_file1 = []
    only_in_file2 = []
    in_both_files = []
    unique_particles = []

    total_micrograph_names = len(grouped_df1.groups)
    current_count = 0

    for micrograph_name, group1 in grouped_df1:
        current_count += 1
        print(f"Processing {current_count}/{total_micrograph_names}: {micrograph_name}")

        try:
            group2 = grouped_df2.get_group(micrograph_name).copy()
        except KeyError:
            only_in_file1.extend(group1.to_dict('records'))
            continue

        indices_to_drop = set()

        for index1, row1 in group1.iterrows():
            x1, y1 = row1['_rlnCoordinateX'], row1['_rlnCoordinateY']
            found_in_both = False

            for index2, row2 in group2.iterrows():
                x2, y2 = row2['_rlnCoordinateX'], row2['_rlnCoordinateY']
                if distance(x1, y1, x2, y2) <= args.radius:
                    in_both_files.append(row1.to_dict())
                    indices_to_drop.add(index2)
                    found_in_both = True
                    break
                    
            if not found_in_both:
                only_in_file1.append(row1.to_dict())

        group2.drop(indices_to_drop, inplace=True)
        only_in_file2.extend(group2.to_dict('records'))

    # After exiting the loop, combine all lists into the unique_particles list
    unique_particles.extend(only_in_file1)
    unique_particles.extend(only_in_file2)
    unique_particles.extend(in_both_files)

    # Writing data frames to star files
    write_star(optics_header1, df1, particles_header1, pd.DataFrame(only_in_file1), 'star1.star')
    write_star(optics_header2, df2, particles_header2, pd.DataFrame(only_in_file2), 'star2.star')
    write_star(optics_header1, df1, particles_header1, pd.DataFrame(in_both_files), 'combined.star')
    write_star(optics_header1, df1, particles_header1, pd.DataFrame(unique_particles), 'unique.star')

    # Print the number of particles in each output file
    print(f"Output file details:")
    print(f"star1.star: {len(only_in_file1)} particles")
    print(f"star2.star: {len(only_in_file2)} particles")
    print(f"combined.star: {len(in_both_files)} particles")
    print(f"unique.star: {len(unique_particles)} particles")

if __name__ == '__main__':
    main()
