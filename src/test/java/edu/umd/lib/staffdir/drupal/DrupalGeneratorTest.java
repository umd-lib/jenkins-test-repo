package edu.umd.lib.staffdir.drupal;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;

import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.junit.Before;
import org.junit.Test;

import edu.umd.lib.staffdir.JsonUtils;
import edu.umd.lib.staffdir.Person;
import edu.umd.lib.staffdir.TestUtils;

public class DrupalGeneratorTest {
  private DrupalGenerator drupalGenerator;

  @Before
  public void setUp() throws Exception {
    List<Map<String, String>> fieldMappings = TestUtils.fromCsvFile(
        "src/test/resources/drupal/drupalMappings.csv");
    drupalGenerator = new DrupalGenerator(fieldMappings);
  }

  @Test
  public void testGetDisplayValue_nullValues() {
    assertNull(drupalGenerator.getDisplayValue(null, null));
  }

  @Test
  public void testGetDisplayValue_unknownDisplayType() {
    String displayType = "UNKNOWN_DISPLAY_TYPE";

    // Values for unknown display types are returned unchanged
    assertNull(drupalGenerator.getDisplayValue(displayType, null));
    assertEquals("", drupalGenerator.getDisplayValue(displayType, ""));
    assertEquals("Value", drupalGenerator.getDisplayValue(displayType, "Value"));
  }

  @Test
  public void testGetDisplayValue_textDisplayType() {
    String displayType = "Text";

    // All values get returned unchanged
    assertNull(drupalGenerator.getDisplayValue(displayType, null));
    assertEquals("", drupalGenerator.getDisplayValue(displayType, ""));
    assertEquals("Value", drupalGenerator.getDisplayValue(displayType, "Value"));
  }

  @Test
  public void testPersonToMap() throws Exception {
    List<Person> testPersons = getTestPersons();

    String[] drupalPersonMapKeys = {
        "directory_id", "division", "department", "unit",
        "last_name", "first_name", "phone", "email", "title", "display_name",
        "location"
    };

    Person p = testPersons.get(0);
    Map<String, String> drupalPersonMap = drupalGenerator.personToMap(p);

    Set<String> expectedKeys = new HashSet<>(Arrays.asList(drupalPersonMapKeys));
    assertEquals(expectedKeys, drupalPersonMap.keySet());
    assertEquals("testperson1", drupalPersonMap.get("directory_id"));
    assertEquals("Digital Service and Technologies", drupalPersonMap.get("division"));
    assertEquals("Software Systems Development and Research", drupalPersonMap.get("department"));
    assertEquals("", drupalPersonMap.get("unit"));
    assertEquals("Person1", drupalPersonMap.get("last_name"));
    assertEquals("Test", drupalPersonMap.get("first_name"));
    assertEquals("+1 555 123 4567", drupalPersonMap.get("phone"));
    assertEquals("testperson1@example.com", drupalPersonMap.get("email"));
    assertEquals("Display Tester Level 1", drupalPersonMap.get("title"));
    assertEquals("Test Person1", drupalPersonMap.get("display_name"));
    assertEquals("Test Room 1 Test Building 1", drupalPersonMap.get("location"));
  }

  @Test
  public void testGetTitle_noFunctionalTitle_noOfficialTitle() throws Exception {
    List<Person> testPersons = getTestPersons();
    TestPerson testPerson = new TestPerson(testPersons.get(0));
    testPerson.setField("Staff", "Functional Title", null);
    testPerson.setField("LDAP", "umDisplayTitle", "LDAP umDisplayTitle");
    testPerson.setField("LDAP", "umOfficialTitle", "");

    String title = drupalGenerator.getTitle(testPerson);
    assertEquals("LDAP umDisplayTitle", title);
  }

  @Test
  public void testGetTitle_hasFunctionalTitle_noOfficialTitle() throws Exception {
    List<Person> testPersons = getTestPersons();
    TestPerson testPerson = new TestPerson(testPersons.get(0));
    testPerson.setField("Staff", "Functional Title", "Staff Functional Title");
    testPerson.setField("LDAP", "umDisplayTitle", "LDAP umDisplayTitle");
    testPerson.setField("LDAP", "umOfficialTitle", "");

    String title = drupalGenerator.getTitle(testPerson);
    assertEquals("Staff Functional Title", title);
  }

  @Test
  public void testGetTitle_noFunctionalTitle_LibrarianOfficialTitle() throws Exception {
    List<Person> testPersons = getTestPersons();
    TestPerson testPerson = new TestPerson(testPersons.get(0));
    testPerson.setField("Staff", "Functional Title", "");
    testPerson.setField("LDAP", "umDisplayTitle", "LDAP umDisplayTitle");
    testPerson.setField("LDAP", "umOfficialTitle", "Librarian I");

    String title = drupalGenerator.getTitle(testPerson);
    assertEquals("LDAP umDisplayTitle (Librarian I)", title);
  }

  @Test
  public void testGetTitle_noFunctionalTitle_NotLibrarianOfficialTitle() throws Exception {
    List<Person> testPersons = getTestPersons();
    TestPerson testPerson = new TestPerson(testPersons.get(0));
    testPerson.setField("Staff", "Functional Title", "");
    testPerson.setField("LDAP", "umDisplayTitle", "LDAP umDisplayTitle");
    testPerson.setField("LDAP", "umOfficialTitle", "Janitor");

    String title = drupalGenerator.getTitle(testPerson);
    assertEquals("LDAP umDisplayTitle", title);
  }

  @Test
  public void testGetTitle_suppress_LibrarianOfficialTitle_if_matches_Title() throws Exception {
    List<Person> testPersons = getTestPersons();
    TestPerson testPerson = new TestPerson(testPersons.get(0));
    testPerson.setField("Staff", "Functional Title", "");
    testPerson.setField("LDAP", "umDisplayTitle", "Librarian II");
    testPerson.setField("LDAP", "umOfficialTitle", "Librarian II");

    String title = drupalGenerator.getTitle(testPerson);
    assertEquals("Librarian II", title);
  }

  @Test
  public void testGetLocation_noRoom_noBuilding() throws Exception {
    List<Person> testPersons = getTestPersons();
    TestPerson testPerson = new TestPerson(testPersons.get(0));
    testPerson.setField("LDAP", "umPrimaryCampusRoom", "");
    testPerson.setField("LDAP", "umPrimaryCampusBuilding", "");

    String location = drupalGenerator.getLocation(testPerson);
    assertEquals("", location);
  }

  @Test
  public void testGetLocation_noRoom_hasBuilding() throws Exception {
    List<Person> testPersons = getTestPersons();
    TestPerson testPerson = new TestPerson(testPersons.get(0));
    testPerson.setField("LDAP", "umPrimaryCampusRoom", "");
    testPerson.setField("LDAP", "umPrimaryCampusBuilding", "Test Building");

    String location = drupalGenerator.getLocation(testPerson);
    assertEquals("Test Building", location);
  }

  @Test
  public void testGetLocation_hasRoom_hasBuilding() throws Exception {
    List<Person> testPersons = getTestPersons();
    TestPerson testPerson = new TestPerson(testPersons.get(0));
    testPerson.setField("LDAP", "umPrimaryCampusRoom", "Test Room");
    testPerson.setField("LDAP", "umPrimaryCampusBuilding", "Test Building");

    String location = drupalGenerator.getLocation(testPerson);
    assertEquals("Test Room Test Building", location);
  }

  @Test
  public void testGetLocation_hasRoom_noBuilding() throws Exception {
    List<Person> testPersons = getTestPersons();
    TestPerson testPerson = new TestPerson(testPersons.get(0));
    testPerson.setField("LDAP", "umPrimaryCampusRoom", "Test Room");
    testPerson.setField("LDAP", "umPrimaryCampusBuilding", "");

    String location = drupalGenerator.getLocation(testPerson);
    assertEquals("Test Room", location);
  }

  @Test
  public void testIntegrationTest() throws Exception {
    String expectedOutput = new String(
        Files.readAllBytes(Paths.get("src/test/resources/drupal/expected_drupal_output.json")), StandardCharsets.UTF_8);

    List<Person> testPersons = getTestPersons();
    ByteArrayOutputStream out = new ByteArrayOutputStream();

    drupalGenerator.generate(out, testPersons);
    assertEquals(expectedOutput, out.toString("utf-8"));
  }

  private List<Person> getTestPersons() {
    return JsonUtils.readFromJson("src/test/resources/drupal/test_persons.json");
  }

  class TestPerson extends Person {
    public TestPerson(Person person) {
      super(person.uid, person.sources);
    }

    public void setField(String sourcesKey, String fieldKey, String fieldValue) {
      Map<String, String> sourceMap = sources.get(sourcesKey);
      if (!sourceMap.containsKey(fieldKey) && !fieldKey.equals("Functional Title")) {
        throw new IllegalArgumentException(String.format("Unknown key '%s' for sourceMap '%s'", fieldKey, sourcesKey));
      }
      sourceMap.put(fieldKey, fieldValue);
    }
  }
}
