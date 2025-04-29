function uuidv4(){
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'
      .replace(/[xy]/g,c=>{
        let r=(Math.random()*16)|0, v=c=='x'?r:(r&0x3|0x8);
        return v.toString(16);
      });
  }
  
  function app(){
    return {
      userType: 'FrontDeskOfficer',
      jenisList: [
        { id: uuidv4(), nama: 'Kucing' },
        { id: uuidv4(), nama: 'Anjing' }
      ],
      klienList: [
        { id: uuidv4(), nama: 'John Doe' },
        { id: uuidv4(), nama: 'PT Aku Sayang Hewan' },
        { id: uuidv4(), nama: 'PT Pecinta Kucing' }
      ],
      hewanList: [],
      petToDelete: null,
  
      // Jenis
      showJenisForm: false,
      editingJenis: false,
      jenisForm: { id:'', nama:'' },
      resetJenisForm(){
        this.editingJenis=false;
        this.jenisForm={id:'',nama:''};
      },
      addJenis(){
        if(!this.jenisForm.nama) return;
        this.jenisList.push({id:uuidv4(),nama:this.jenisForm.nama});
        this.showJenisForm=false;
      },
      startEditJenis(j){
        this.editingJenis=true;
        this.jenisForm={...j};
        this.showJenisForm=true;
      },
      updateJenis(){
        let i=this.jenisList.findIndex(x=>x.id===this.jenisForm.id);
        if(i>-1) this.jenisList[i].nama=this.jenisForm.nama;
        this.showJenisForm=false;
      },
      deleteJenis(id){
        if(!confirm('Hapus jenis ini?')) return;
        this.jenisList=this.jenisList.filter(x=>x.id!==id);
      },
  
      // Hewan Peliharaan
      showHewanForm: false,
      editingHewan: false,
      hewanForm: { id:'', pemilik:'', jenis:'', nama:'', tanggal_lahir:'', url:'' },
      resetHewanForm(){
        this.editingHewan=false;
        this.hewanForm={
          id: '',
          pemilik: this.klienList[0].id,
          jenis: this.jenisList[0].id,
          nama: '',
          tanggal_lahir: '',
          url: ''
        };
      },
      addHewan(){
        if(!this.hewanForm.nama) return;
        this.hewanList.push({...this.hewanForm, id: uuidv4()});
        this.showHewanForm=false;
      },
      startEditHewan(h){
        this.editingHewan=true;
        this.hewanForm={...h};
        this.showHewanForm=true;
      },
      updateHewan(){
        let i=this.hewanList.findIndex(x=>x.id===this.hewanForm.id);
        if(i>-1) this.hewanList[i]={...this.hewanForm};
        this.showHewanForm=false;
      },
      prepareDeletePet(h){
        this.petToDelete = h;
      },
      cancelDeletePet(){
        this.petToDelete = null;
      },
      confirmDeletePet(){
        this.hewanList = this.hewanList.filter(x=>x.id!==this.petToDelete.id);
        this.petToDelete = null;
      },
  
      // Helpers
      findKlien(id){ return this.klienList.find(x=>x.id===id) || {}; },
      findJenis(id){ return this.jenisList.find(x=>x.id===id) || {}; },
      formatDate(dateStr){
        const d = new Date(dateStr);
        return d.toLocaleDateString('id-ID', {
          day: 'numeric', month: 'long', year: 'numeric'
        });
      }
    }
  }
  