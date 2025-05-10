import os
import re
import markdown
from pathlib import Path

def check_markdown_links(file_path):
    """Check for broken links in markdown files."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all markdown links
    links = re.findall(r'\[(.*?)\]\((.*?)\)', content)
    
    broken_links = []
    for text, link in links:
        # Skip external links
        if link.startswith('http'):
            continue
            
        # Convert relative paths to absolute
        abs_link = os.path.join(os.path.dirname(file_path), link)
        
        # Check if file exists
        if not os.path.exists(abs_link):
            broken_links.append((text, link))
    
    return broken_links

def check_documentation_coverage():
    """Check if all documentation files are properly linked."""
    docs_dir = Path('docs')
    
    # Get all markdown files
    markdown_files = list(docs_dir.rglob('*.md'))
    
    # Create a set of all files
    all_files = set(str(f.relative_to(docs_dir)) for f in markdown_files)
    
    # Check each file for links
    for file in markdown_files:
        broken_links = check_markdown_links(file)
        if broken_links:
            print(f"\nBroken links in {file.relative_to(docs_dir)}:")
            for text, link in broken_links:
                print(f"- [{text}]({link})")
    
    # Check for orphaned files
    referenced_files = set()
    for file in markdown_files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        links = re.findall(r'\[(.*?)\]\((.*?)\)', content)
        for _, link in links:
            if not link.startswith('http'):
                abs_link = os.path.join(os.path.dirname(file), link)
                rel_link = os.path.relpath(abs_link, docs_dir)
                referenced_files.add(rel_link)
    
    orphaned_files = all_files - referenced_files
    if orphaned_files:
        print("\nOrphaned files:")
        for file in orphaned_files:
            print(f"- {file}")

if __name__ == "__main__":
    print("Checking documentation...")
    check_documentation_coverage()
    print("\nDocumentation check complete.")
